import json
import logging
from typing import Dict, List, Optional
from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from openai import OpenAI

from .models import ChatSession, ChatMessage, LearningPreference, ChatbotKnowledgeBase

logger = logging.getLogger(__name__)

class ChatbotService:
    def __init__(self, user, session_id=None):
        self.user = user
        self.session = self._get_or_create_session(session_id)
        self.learning_prefs = self._get_learning_preferences()
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
    def _get_or_create_session(self, session_id=None) -> ChatSession:
        """Retrieve an existing session or create a new one"""
        if session_id:
            try:
                return ChatSession.objects.get(id=session_id, user=self.user, is_active=True)
            except ChatSession.DoesNotExist:
                pass
                
        # Create a new session
        return ChatSession.objects.create(user=self.user)
    
    def _get_learning_preferences(self) -> LearningPreference:
        """Get or create learning preferences for the user"""
        return LearningPreference.objects.get_or_create(user=self.user)[0]
    
    def _get_system_prompt(self) -> str:
        """Generate system prompt based on user's learning preferences"""
        prefs = self.learning_prefs
        
        # Base system prompt
        prompt = """You are an AI teaching assistant designed to help students with their learning. 
        You are patient, encouraging, and adapt your teaching style to the student's needs.
        """
        
        # Add learning condition specific instructions
        if prefs.learning_condition == 'ADHD':
            prompt += """
            The student has ADHD. Please:
            - Keep responses concise and to the point
            - Use bullet points and short paragraphs
            - Provide clear, structured information
            - Use engaging language and examples
            - Suggest movement breaks if the session is long
            """
        elif prefs.learning_condition == 'DYSLEXIA':
            prompt += """
            The student has dyslexia. Please:
            - Use simple, clear language
            - Break down complex concepts into smaller parts
            - Use examples and analogies
            - Be patient and encouraging
            - Offer to read text aloud if needed
            """
            
        # Add response style preferences
        if prefs.response_style == 'CONCISE':
            prompt += "\nThe student prefers concise, to-the-point responses."
        elif prefs.response_style == 'DETAILED':
            prompt += "\nThe student prefers detailed, thorough explanations."
        elif prefs.response_style == 'STEP_BY_STEP':
            prompt += "\nThe student prefers step-by-step guidance with clear instructions."
        elif prefs.response_style == 'VISUAL':
            prompt += "\nThe student prefers visual explanations. Include markdown formatting, diagrams, or suggest visual aids when possible."
            
        return prompt.strip()
    
    def _get_chat_history(self, limit=10) -> List[Dict]:
        """Get recent chat history for context"""
        messages = []
        for msg in self.session.messages.order_by('-created_at')[:limit]:
            messages.insert(0, {"role": msg.role, "content": msg.content})
        return messages
    
    def _get_relevant_knowledge(self, query: str) -> List[Dict]:
        """Retrieve relevant knowledge base entries for the query"""
        # Simple keyword-based search - could be enhanced with vector search
        from django.db.models import Q
        
        # Split query into keywords
        keywords = query.lower().split()
        
        # Build OR query for all keywords
        query_filter = Q()
        for keyword in keywords:
            if len(keyword) > 2:  # Ignore very short keywords
                query_filter |= Q(title__icontains=keyword) | Q(content__icontains=keyword)
        
        # Filter by active entries and user's learning condition
        relevant = ChatbotKnowledgeBase.objects.filter(
            query_filter,
            is_active=True,
            target_conditions__contains=[self.learning_prefs.learning_condition]
        ).order_by('?')[:3]  # Get up to 3 random relevant entries
        
        return [{"title": kb.title, "content": kb.content} for kb in relevant]
    
    def generate_response(self, user_message: str) -> Dict:
        """Generate a response to the user's message"""
        try:
            # Create user message in database
            user_msg = ChatMessage.objects.create(
                session=self.session,
                role='user',
                message_type='text',
                content=user_message
            )
            
            # Get relevant knowledge base entries
            knowledge = self._get_relevant_knowledge(user_message)
            
            # Prepare messages for the LLM
            messages = [
                {"role": "system", "content": self._get_system_prompt()}
            ]
            
            # Add knowledge base context if available
            if knowledge:
                knowledge_text = "\n\n".join([f"{k['title']}: {k['content']}" for k in knowledge])
                messages.append({
                    "role": "system", 
                    "content": f"Here is some relevant information that might help answer the question:\n\n{knowledge_text}"
                })
            
            # Add chat history
            messages.extend(self._get_chat_history())
            
            # Add the current user message
            messages.append({"role": "user", "content": user_message})
            
            # Generate response using OpenAI
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.7,
                max_tokens=1000,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0,
            )
            
            # Extract the response text
            bot_response = response.choices[0].message.content
            
            # Save bot response to database
            bot_msg = ChatMessage.objects.create(
                session=self.session,
                role='assistant',
                message_type='text',
                content=bot_response,
                parent=user_msg
            )
            
            # Update session timestamp
            self.session.updated_at = timezone.now()
            self.session.save()
            
            return {
                'success': True,
                'response': bot_response,
                'message_id': str(bot_msg.id),
                'session_id': str(self.session.id)
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': "Sorry, I encountered an error processing your request. Please try again."
            }


def create_break_reminder(user):
    """Create a friendly break reminder message"""
    try:
        prefs = LearningPreference.objects.get(user=user)
        
        if not prefs.enable_break_reminders:
            return None
            
        # Get last activity time
        last_activity = ChatMessage.objects.filter(
            session__user=user,
            role='user'
        ).order_by('-created_at').first()
        
        if last_activity and (timezone.now() - last_activity.created_at) >= timedelta(minutes=prefs.break_interval):
            return "Would you like to take a short break? It's been a while since your last one!"
            
    except Exception as e:
        logger.error(f"Error creating break reminder: {str(e)}")
        
    return None

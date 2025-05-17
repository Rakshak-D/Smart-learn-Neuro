import json
import logging
from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import ChatSession, ChatMessage, LearningPreference, UserFeedback, ChatbotKnowledgeBase
from .serializers import (
    ChatSessionSerializer, ChatMessageSerializer, 
    LearningPreferenceSerializer, UserFeedbackSerializer,
    ChatbotKnowledgeBaseSerializer
)
from .services import ChatbotService, create_break_reminder

logger = logging.getLogger(__name__)

# API Views
class ChatSessionViewSet(viewsets.ModelViewSet):
    """ViewSet for managing chat sessions"""
    serializer_class = ChatSessionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ChatSession.objects.filter(user=self.request.user, is_active=True).order_by('-updated_at')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        """Mark a chat session as inactive"""
        session = self.get_object()
        session.is_active = False
        session.save()
        return Response({'status': 'session closed'}, status=status.HTTP_200_OK)


class ChatMessageViewSet(viewsets.ModelViewSet):
    """ViewSet for managing chat messages"""
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        session_id = self.request.query_params.get('session_id')
        if session_id:
            return ChatMessage.objects.filter(
                session_id=session_id, 
                session__user=self.request.user
            ).order_by('created_at')
        return ChatMessage.objects.none()
    
    def create(self, request, *args, **kwargs):
        """Create a new chat message and get a response"""
        session_id = request.data.get('session_id')
        message = request.data.get('message', '').strip()
        
        if not message:
            return Response(
                {'error': 'Message cannot be empty'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Initialize chatbot service
            chatbot = ChatbotService(user=request.user, session_id=session_id)
            
            # Generate response
            result = chatbot.generate_response(message)
            
            if result['success']:
                return Response(result, status=status.HTTP_200_OK)
            else:
                return Response(
                    {'error': result.get('error', 'Failed to generate response')}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Exception as e:
            logger.error(f"Error in chat: {str(e)}", exc_info=True)
            return Response(
                {'error': 'An error occurred while processing your request'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LearningPreferenceViewSet(viewsets.ModelViewSet):
    """ViewSet for managing learning preferences"""
    serializer_class = LearningPreferenceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return LearningPreference.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    def get_object(self):
        # Get or create preferences for the user
        obj, created = LearningPreference.objects.get_or_create(user=self.request.user)
        return obj


class UserFeedbackViewSet(viewsets.ModelViewSet):
    """ViewSet for managing user feedback"""
    serializer_class = UserFeedbackSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return UserFeedback.objects.filter(user=self.request.user).order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ChatbotKnowledgeBaseViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for accessing the chatbot knowledge base"""
    serializer_class = ChatbotKnowledgeBaseSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ChatbotKnowledgeBase.objects.filter(is_active=True)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search the knowledge base"""
        query = request.query_params.get('q', '').strip()
        if not query:
            return Response(
                {'error': 'Search query is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Simple search - could be enhanced with vector search
        results = ChatbotKnowledgeBase.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query),
            is_active=True
        )
        
        serializer = self.get_serializer(results, many=True)
        return Response(serializer.data)


# Regular Django views
@login_required
def chat_interface(request, session_id=None):
    """Render the main chat interface"""
    context = {
        'session_id': session_id,
        'learning_conditions': dict(LearningPreference.LEARNING_CONDITION_CHOICES),
        'response_styles': dict(LearningPreference.RESPONSE_STYLE_CHOICES),
    }
    return render(request, 'chatbot/chat.html', context)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_break_reminder(request):
    """Check if the user should take a break"""
    reminder = create_break_reminder(request.user)
    if reminder:
        return Response({'reminder': reminder})
    return Response({})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def process_voice_input(request):
    """Process voice input from the user"""
    if 'audio' not in request.FILES:
        return Response(
            {'error': 'No audio file provided'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    audio_file = request.FILES['audio']
    
    try:
        # Here you would typically send the audio to a speech-to-text service
        # For example, using OpenAI's Whisper API:
        # response = openai.Audio.transcribe("whisper-1", audio_file)
        # text = response['text']
        
        # For now, we'll return a placeholder
        return Response({
            'text': 'This is a placeholder for the transcribed text from the audio.'
        })
        
    except Exception as e:
        logger.error(f"Error processing voice input: {str(e)}", exc_info=True)
        return Response(
            {'error': 'Failed to process voice input'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

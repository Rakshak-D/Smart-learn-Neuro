"""
WebSocket consumers for the AI app.
"""
import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

from .models import LearningSession
from .tasks import update_learning_analytics_task, process_adaptive_assessment

User = get_user_model()
logger = logging.getLogger(__name__)


class AnalyticsConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time learning analytics.
    """
    
    async def connect(self):
        """Handle WebSocket connection."""
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.room_group_name = f'analytics_{self.user_id}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        logger.info(f"WebSocket connected for analytics (user: {self.user_id})")
        
        # Send initial data
        await self.send_analytics_update()
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        logger.info(f"WebSocket disconnected (user: {self.user_id}, code: {close_code})")
    
    async def receive(self, text_data):
        """Handle WebSocket message."""
        try:
            data = json.loads(text_data)
            action = data.get('action')
            
            if action == 'refresh':
                await self.send_analytics_update()
            else:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Invalid action'
                }))
                
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))
    
    async def analytics_update(self, event):
        """Send analytics update to the client."""
        await self.send(text_data=json.dumps({
            'type': 'analytics.update',
            'data': event['data']
        }))
    
    async def send_analytics_update(self):
        """Fetch and send updated analytics data."""
        try:
            # Call the async version of the task
            result = await database_sync_to_async(update_learning_analytics_task.delay)(self.user_id)
            data = result.get()  # This will block until the task is done
            
            await self.send(text_data=json.dumps({
                'type': 'analytics.update',
                'data': data
            }))
            
        except Exception as e:
            logger.error(f"Error sending analytics update: {str(e)}", exc_info=True)
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Failed to update analytics'
            }))


class LearningSessionConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for adaptive learning sessions.
    """
    
    async def connect(self):
        """Handle WebSocket connection."""
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.room_group_name = f'session_{self.session_id}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        logger.info(f"Learning session WebSocket connected (session: {self.session_id})")
        
        # Send session data
        await self.send_session_update()
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        logger.info(f"Learning session WebSocket disconnected (session: {self.session_id}, code: {close_code})")
    
    async def receive(self, text_data):
        """Handle WebSocket message."""
        try:
            data = json.loads(text_data)
            action = data.get('action')
            
            if action == 'update_progress':
                await self.update_lesson_progress(data.get('lesson_id'), data.get('progress'))
            elif action == 'complete_lesson':
                await self.complete_lesson(data.get('lesson_id'), data.get('feedback', ''))
            elif action == 'get_session_data':
                await self.send_session_update()
            else:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Invalid action'
                }))
                
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))
    
    async def session_update(self, event):
        """Send session update to the client."""
        await self.send(text_data=json.dumps({
            'type': 'session.update',
            'data': event['data']
        }))
    
    async def send_session_update(self):
        """Fetch and send updated session data."""
        try:
            session = await self.get_session()
            if session:
                await self.send(text_data=json.dumps({
                    'type': 'session.update',
                    'data': {
                        'session_id': str(session.id),
                        'status': session.status,
                        'progress': session.progress,
                        'current_lesson': session.current_lesson,
                        'started_at': session.started_at.isoformat() if session.started_at else None,
                        'completed_at': session.completed_at.isoformat() if session.completed_at else None,
                    }
                }))
            else:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Session not found'
                }))
                
        except Exception as e:
            logger.error(f"Error sending session update: {str(e)}", exc_info=True)
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Failed to update session'
            }))
    
    @database_sync_to_async
    def get_session(self):
        """Get the learning session from the database."""
        try:
            return LearningSession.objects.get(id=self.session_id)
        except LearningSession.DoesNotExist:
            return None
    
    @database_sync_to_async
    def update_lesson_progress(self, lesson_id, progress):
        """Update lesson progress in the database."""
        try:
            session = LearningSession.objects.get(id=self.session_id)
            # Update progress logic here
            session.progress = progress
            session.save()
            return True
        except (LearningSession.DoesNotExist, ValueError):
            return False
    
    @database_sync_to_async
    def complete_lesson(self, lesson_id, feedback=''):
        """Mark a lesson as completed in the database."""
        try:
            session = LearningSession.objects.get(id=self.session_id)
            # Complete lesson logic here
            session.completed_lessons.append(lesson_id)
            session.progress = min(100, session.progress + (100 / session.total_lessons))
            
            if session.progress >= 100:
                session.status = 'completed'
                session.completed_at = timezone.now()
            
            session.save()
            return True
        except (LearningSession.DoesNotExist, ValueError):
            return False


class AssessmentConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time assessment monitoring.
    """
    
    async def connect(self):
        """Handle WebSocket connection."""
        self.attempt_id = self.scope['url_route']['kwargs']['attempt_id']
        self.room_group_name = f'assessment_{self.attempt_id}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        logger.info(f"Assessment WebSocket connected (attempt: {self.attempt_id})")
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        logger.info(f"Assessment WebSocket disconnected (attempt: {self.attempt_id}, code: {close_code})")
    
    async def receive(self, text_data):
        """Handle WebSocket message."""
        try:
            data = json.loads(text_data)
            action = data.get('action')
            
            if action == 'submit_answer':
                await self.submit_answer(
                    data.get('question_id'), 
                    data.get('answer'),
                    data.get('time_taken', 0)
                )
            elif action == 'complete_assessment':
                await self.complete_assessment()
            else:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Invalid action'
                }))
                
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))
    
    async def assessment_update(self, event):
        """Send assessment update to the client."""
        await self.send(text_data=json.dumps({
            'type': 'assessment.update',
            'data': event['data']
        }))
    
    async def submit_answer(self, question_id, answer, time_taken):
        """Submit an answer for the current question."""
        try:
            # Process the answer asynchronously
            result = await database_sync_to_async(process_adaptive_assessment.delay)(
                self.attempt_id, question_id, answer, time_taken
            )
            
            # Get the result (this will block until the task is done)
            result_data = result.get()
            
            if result_data.get('status') == 'success':
                await self.send(text_data=json.dumps({
                    'type': 'answer.submitted',
                    'data': {
                        'question_id': question_id,
                        'is_correct': result_data.get('is_correct', False),
                        'feedback': result_data.get('feedback', ''),
                        'next_question': result_data.get('next_question')
                    }
                }))
                
                # If there's a next question, send it to the client
                next_question = result_data.get('next_question')
                if next_question:
                    await self.send(text_data=json.dumps({
                        'type': 'next_question',
                        'data': next_question
                    }))
            else:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': result_data.get('message', 'Failed to process answer')
                }))
                
        except Exception as e:
            logger.error(f"Error submitting answer: {str(e)}", exc_info=True)
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Failed to submit answer'
            }))
    
    async def complete_assessment(self):
        """Mark the assessment as completed."""
        try:
            # Process the completion asynchronously
            result = await database_sync_to_async(process_adaptive_assessment.delay)(self.attempt_id)
            
            # Get the result (this will block until the task is done)
            result_data = result.get()
            
            if result_data.get('status') == 'success':
                await self.send(text_data=json.dumps({
                    'type': 'assessment.completed',
                    'data': {
                        'score': result_data.get('score'),
                        'correct_answers': result_data.get('correct_answers'),
                        'total_questions': result_data.get('total_questions'),
                        'feedback': result_data.get('feedback', [])
                    }
                }))
            else:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': result_data.get('message', 'Failed to complete assessment')
                }))
                
        except Exception as e:
            logger.error(f"Error completing assessment: {str(e)}", exc_info=True)
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Failed to complete assessment'
            }))

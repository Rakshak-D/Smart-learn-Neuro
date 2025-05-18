import json
import logging
from datetime import datetime, timedelta

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework.reverse import reverse
from django.http import JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404
from django.db.models import Count, Avg, Q, Sum, F, ExpressionWrapper, FloatField
from django.contrib.auth import get_user_model
from django.utils import timezone

# Import models using get_model to avoid circular imports
from django.apps import apps

# Local imports
from .models import LearningSession, LearningAnalytics, AdaptiveLearningProfile
from .serializers import (
    LearningAnalyticsSerializer, 
    LearningPathSerializer,
    LearningPathStepSerializer,
    LessonSerializer,
    TopicSerializer
)
from .adaptive_learning_engine import AdaptiveLearningEngine
from .tasks import (
    update_learning_analytics_task,
    generate_lesson_plan_task,
    analyze_learning_style_task,
    generate_weekly_report,
    process_adaptive_assessment
)

from .adaptive_learning_engine import AdaptiveLearningEngine
from django.apps import apps

# Get models using string references to avoid circular imports
Lesson = apps.get_model('lessons', 'Lesson')
Topic = apps.get_model('lessons', 'Topic')
LessonProgress = apps.get_model('lessons', 'LessonProgress')
Assessment = apps.get_model('assessments', 'Assessment')
AssessmentAttempt = apps.get_model('assessments', 'AssessmentAttempt')
Question = apps.get_model('assessments', 'Question')
UserResponse = apps.get_model('assessments', 'UserResponse')
CustomUser = apps.get_model('users', 'CustomUser')

User = get_user_model()
logger = logging.getLogger(__name__)


@api_view(['GET'])
@renderer_classes([JSONRenderer, BrowsableAPIRenderer])
def api_root(request, format=None):
    """
    API root endpoint that provides links to all available endpoints.
    """
    return Response({
        'learning': {
            'learning_path': reverse('learning_path', request=request, format=format),
            'learning_analytics': reverse('learning_analytics', request=request, format=format),
            'lesson_recommendations': reverse('lesson_recommendations', request=request, format=format),
            'update_learning_profile': reverse('update_learning_profile', request=request, format=format),
            'track_lesson_completion': reverse('track_lesson_completion', request=request, format=format),
            'assessments': reverse('assessments_list', request=request, format=format),
        },
        'speech': {
            'tts_convert': reverse('tts_convert', request=request, format=format),
            'tts_voices': reverse('tts_voices', request=request, format=format),
            'tts_settings': reverse('tts_settings', request=request, format=format),
            'stt_transcribe': reverse('stt_transcribe', request=request, format=format),
            'stt_languages': reverse('stt_languages', request=request, format=format),
        },
        'vision': {
            'face_detection': reverse('face_detection', request=request, format=format),
            'gesture_recognition': reverse('gesture_recognition', request=request, format=format),
            'emotion_detection': reverse('emotion_detection', request=request, format=format),
        },
        'moderation': {
            'moderate_text': reverse('moderate_text', request=request, format=format),
            'moderate_image': reverse('moderate_image', request=request, format=format),
            'moderate_video': reverse('moderate_video', request=request, format=format),
        },
        'analytics': {
            'engagement_analytics': reverse('engagement_analytics', request=request, format=format),
            'performance_analytics': reverse('performance_analytics', request=request, format=format),
            'completion_analytics': reverse('completion_analytics', request=request, format=format),
        },
        'authentication': {
            'token_refresh': reverse('token_refresh', request=request, format=format),
        },
        'documentation': reverse('api-docs', request=request, format=format),
        'schema': reverse('openapi-schema', request=request, format=format),
    })

class LearningPathView(APIView):
    """
    API endpoint for retrieving a personalized learning path for the user.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """
        Get the user's personalized learning path.
        
        Returns:
            Response: JSON response containing the learning path data
        """
        try:
            user = request.user
            
            # Initialize the adaptive learning engine
            engine = AdaptiveLearningEngine(user)
            
            # Get recommended lessons (limit to 5 by default)
            recommended_lessons = engine.get_recommended_lessons(limit=5)
            
            # Serialize the lessons
            lesson_serializer = LessonSerializer(recommended_lessons, many=True)
            
            # Get user's learning style
            learning_style = {}
            try:
                profile = AdaptiveLearningProfile.objects.get(user=user)
                learning_style = {
                    'visual': profile.visual_score,
                    'auditory': profile.auditory_score,
                    'reading_writing': profile.reading_writing_score,
                    'kinesthetic': profile.kinesthetic_score
                }
            except AdaptiveLearningProfile.DoesNotExist:
                pass
            
            # Prepare the response
            response_data = {
                'status': 'success',
                'data': {
                    'recommended_lessons': lesson_serializer.data,
                    'learning_style': learning_style,
                    'generated_at': timezone.now().isoformat()
                }
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in LearningPathView: {str(e)}", exc_info=True)
            return Response(
                {'status': 'error', 'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        engine = AdaptiveLearningEngine(request.user)
        learning_path = engine.generate_learning_path()
        return Response({
            'status': 'success',
            'data': learning_path,
            'generated_at': datetime.now().isoformat()
        })


class LearningAnalyticsView(APIView):
    """
    API endpoint for retrieving learning analytics and progress data.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """
        Get learning analytics for the authenticated user.
        
        Returns:
            Response: JSON response containing learning analytics data
        """
        try:
            user = request.user
            
            # Get the last 30 days of analytics
            thirty_days_ago = timezone.now() - timedelta(days=30)
            
            # Get completed lessons in the last 30 days
            completed_lessons = LessonProgress.objects.filter(
                user=user,
                is_completed=True,
                updated_at__gte=thirty_days_ago
            ).select_related('lesson')
            
            # Calculate time spent and completion rate
            total_time_spent = sum(
                progress.time_spent_seconds or 0 
                for progress in completed_lessons
            )
            
            total_lessons = Lesson.objects.count()
            completed_count = completed_lessons.count()
            completion_rate = (completed_count / total_lessons * 100) if total_lessons > 0 else 0
            
            # Get assessment scores
            assessment_scores = AssessmentAttempt.objects.filter(
                user=user,
                completed_at__isnull=False
            ).values('assessment__title').annotate(
                avg_score=Avg('score')
            )
            
            # Get activity by day
            activity_by_day = (
                LessonProgress.objects
                .filter(user=user, updated_at__gte=thirty_days_ago)
                .values('updated_at__date')
                .annotate(
                    time_spent=Sum('time_spent_seconds'),
                    lessons_completed=Count('id', filter=Q(is_completed=True))
                )
                .order_by('updated_at__date')
            )
            
            # Prepare the response
            response_data = {
                'status': 'success',
                'data': {
                    'summary': {
                        'total_time_spent_seconds': total_time_spent,
                        'total_lessons_completed': completed_count,
                        'completion_rate': round(completion_rate, 2),
                        'average_daily_learning_minutes': round(total_time_spent / 30 / 60, 1)  # Average per day
                    },
                    'assessment_scores': list(assessment_scores),
                    'activity_by_day': list(activity_by_day),
                    'last_updated': timezone.now().isoformat()
                }
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in LearningAnalyticsView: {str(e)}", exc_info=True)
            return Response(
                {'status': 'error', 'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        engine = AdaptiveLearningEngine(request.user)
        analytics = engine.get_learning_analytics()
        return Response({
            'status': 'success',
            'data': analytics,
            'retrieved_at': datetime.now().isoformat()
        })


class LessonRecommendationView(APIView):
    """
    API endpoint for getting personalized lesson recommendations.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """
        Get recommended lessons for the user.
        
        Query Parameters:
            limit (int): Maximum number of recommendations to return (default: 5)
            
        Returns:
            Response: JSON response containing recommended lessons
        """
        try:
            user = request.user
            limit = int(request.query_params.get('limit', 5))
            
            # Initialize the adaptive learning engine
            engine = AdaptiveLearningEngine(user)
            
            # Get recommended lessons
            recommended_lessons = engine.get_recommended_lessons(limit=limit)
            
            # Serialize the lessons
            serializer = LessonSerializer(recommended_lessons, many=True)
            
            # Get the user's learning style if available
            learning_style = {}
            try:
                profile = AdaptiveLearningProfile.objects.get(user=user)
                learning_style = {
                    'visual': profile.visual_score,
                    'auditory': profile.auditory_score,
                    'reading_writing': profile.reading_writing_score,
                    'kinesthetic': profile.kinesthetic_score,
                    'primary_style': profile.get_primary_learning_style()
                }
            except AdaptiveLearningProfile.DoesNotExist:
                pass
            
            # Prepare the response
            response_data = {
                'status': 'success',
                'data': {
                    'recommendations': serializer.data,
                    'learning_style': learning_style,
                    'count': len(recommended_lessons),
                    'generated_at': timezone.now().isoformat()
                }
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in LessonRecommendationView: {str(e)}", exc_info=True)
            return Response(
                {'status': 'error', 'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        limit = int(request.query_params.get('limit', 5))
        engine = AdaptiveLearningEngine(request.user)
        recommended_lessons = engine.get_recommended_lessons(limit=limit)
        
        # Format the response
        lessons_data = [{
            'id': lesson.id,
            'title': lesson.title,
            'description': lesson.description,
            'difficulty': lesson.difficulty,
            'duration': lesson.duration,
            'content_type': lesson.content_type,
            'topic': {
                'id': lesson.topic.id,
                'name': lesson.topic.name,
                'subject': lesson.topic.subject
            } if lesson.topic else None,
            'thumbnail': request.build_absolute_uri(lesson.thumbnail.url) if lesson.thumbnail else None
        } for lesson in recommended_lessons]
        
        return Response({
            'status': 'success',
            'count': len(lessons_data),
            'results': lessons_data
        })


class UpdateLearningProfileView(APIView):
    """
    API endpoint for updating the user's learning profile.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """
        Update the user's learning profile based on their interactions.
        
        Expected POST data:
        {
            "learning_style": {
                "visual": 0.7,
                "auditory": 0.5,
                "reading_writing": 0.6,
                "kinesthetic": 0.4
            },
            "preferences": {
                "difficulty_level": "intermediate",
                "content_types": ["video", "interactive"],
                "daily_goal_minutes": 30
            },
            "accessibility_settings": {
                "font_size": "medium",
                "high_contrast": false,
                "text_to_speech": true
            }
        }
        
        Returns:
            Response: JSON response with the updated profile
        """
        try:
            user = request.user
            data = request.data
            
            # Get or create the learning profile
            profile, created = AdaptiveLearningProfile.objects.get_or_create(user=user)
            
            # Update learning style if provided
            if 'learning_style' in data:
                learning_style = data['learning_style']
                for style in ['visual', 'auditory', 'reading_writing', 'kinesthetic']:
                    if style in learning_style:
                        setattr(profile, f'{style}_score', float(learning_style[style]))
            
            # Update preferences if provided
            if 'preferences' in data:
                preferences = data['preferences']
                if 'difficulty_level' in preferences:
                    profile.difficulty_level = preferences['difficulty_level']
                if 'content_types' in preferences and isinstance(preferences['content_types'], list):
                    profile.preferred_content_types = preferences['content_types']
                if 'daily_goal_minutes' in preferences:
                    profile.daily_goal_minutes = int(preferences['daily_goal_minutes'])
            
            # Update accessibility settings if provided
            if 'accessibility_settings' in data:
                accessibility = data['accessibility_settings']
                if 'font_size' in accessibility:
                    profile.font_size = accessibility['font_size']
                if 'high_contrast' in accessibility:
                    profile.high_contrast = bool(accessibility['high_contrast'])
                if 'text_to_speech' in accessibility:
                    profile.text_to_speech = bool(accessibility['text_to_speech'])
            
            # Save the updated profile
            profile.save()
            
            # Prepare the response
            response_data = {
                'status': 'success',
                'message': 'Learning profile updated successfully',
                'data': {
                    'learning_style': {
                        'visual': profile.visual_score,
                        'auditory': profile.auditory_score,
                        'reading_writing': profile.reading_writing_score,
                        'kinesthetic': profile.kinesthetic_score,
                        'primary_style': profile.get_primary_learning_style()
                    },
                    'preferences': {
                        'difficulty_level': profile.difficulty_level,
                        'content_types': profile.preferred_content_types,
                        'daily_goal_minutes': profile.daily_goal_minutes
                    },
                    'accessibility_settings': {
                        'font_size': profile.font_size,
                        'high_contrast': profile.high_contrast,
                        'text_to_speech': profile.text_to_speech
                    },
                    'updated_at': profile.updated_at.isoformat()
                }
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in UpdateLearningProfileView: {str(e)}", exc_info=True)
            return Response(
                {'status': 'error', 'message': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        engine = AdaptiveLearningEngine(request.user)
        updates = engine.update_learning_profile()
        
        return Response({
            'status': 'success',
            'message': 'Learning profile updated successfully',
            'updates': updates,
            'updated_at': datetime.now().isoformat()
        })

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def track_lesson_completion(request):
    """
    Track when a user completes a lesson and update their learning profile.
    
    Expected POST data:
    {
        "lesson_id": 123,
        "time_spent_seconds": 300,
        "completion_percentage": 100,
        "feedback": {
            "difficulty": "just_right",  # too_easy, just_right, too_hard
            "enjoyment_rating": 4,        # 1-5 scale
            "notes": "Optional user feedback"
        }
    }
    
    Returns:
        Response: JSON response with the updated lesson progress
    """
    try:
        user = request.user
        data = request.data
        
        # Validate required fields
        if 'lesson_id' not in data:
            return Response(
                {'status': 'error', 'message': 'lesson_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Get or create the lesson progress
        lesson_id = data['lesson_id']
        time_spent = data.get('time_spent_seconds', 0)
        completion_percentage = min(100, max(0, data.get('completion_percentage', 0)))
        is_completed = completion_percentage >= 90  # Consider 90%+ as completed
        
        # Get the lesson
        try:
            lesson = Lesson.objects.get(id=lesson_id)
        except Lesson.DoesNotExist:
            return Response(
                {'status': 'error', 'message': 'Lesson not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Update or create the lesson progress
        progress, created = LessonProgress.objects.update_or_create(
            user=user,
            lesson=lesson,
            defaults={
                'is_completed': is_completed,
                'completion_percentage': completion_percentage,
                'time_spent_seconds': time_spent,
                'last_accessed': timezone.now()
            }
        )
        
        # Process feedback if provided
        feedback_data = data.get('feedback', {})
        if feedback_data:
            progress.feedback = json.dumps(feedback_data)
            progress.save()
            
            # Update learning style based on feedback (simplified example)
            try:
                profile = AdaptiveLearningProfile.objects.get(user=user)
                enjoyment = feedback_data.get('enjoyment_rating', 3) / 5.0  # Normalize to 0-1
                
                # Simple adjustment to learning style based on lesson type and enjoyment
                # In a real app, this would be more sophisticated
                if lesson.content_type in ['video', 'interactive']:
                    profile.visual_score = min(1.0, profile.visual_score + (0.1 * enjoyment))
                if lesson.content_type in ['audio', 'podcast']:
                    profile.auditory_score = min(1.0, profile.auditory_score + (0.1 * enjoyment))
                if lesson.content_type in ['text', 'article']:
                    profile.reading_writing_score = min(1.0, profile.reading_writing_score + (0.1 * enjoyment))
                if lesson.content_type in ['interactive', 'exercise']:
                    profile.kinesthetic_score = min(1.0, profile.kinesthetic_score + (0.1 * enjoyment))
                    
                profile.save()
            except Exception as e:
                logger.warning(f"Could not update learning style: {str(e)}")
        
        # Update learning analytics asynchronously
        update_learning_analytics_task.delay(user.id)
        
        # Prepare the response
        response_data = {
            'status': 'success',
            'message': 'Lesson progress updated successfully',
            'data': {
                'lesson_id': lesson.id,
                'title': lesson.title,
                'is_completed': progress.is_completed,
                'completion_percentage': progress.completion_percentage,
                'time_spent_seconds': progress.time_spent_seconds,
                'last_accessed': progress.last_accessed.isoformat(),
                'created': created
            }
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in track_lesson_completion: {str(e)}", exc_info=True)
        return Response(
            {'status': 'error', 'message': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    try:
        data = request.data
        lesson_id = data.get('lesson_id')
        time_spent = data.get('time_spent_seconds', 0)
        completion_percentage = data.get('completion_percentage', 100)
        
        # Get the lesson
        try:
            lesson = Lesson.objects.get(id=lesson_id, is_published=True)
        except Lesson.DoesNotExist:
            return Response(
                {'error': 'Lesson not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Create or update lesson progress
        progress, created = LessonProgress.objects.update_or_create(
            user=request.user,
            lesson=lesson,
            defaults={
                'is_completed': completion_percentage >= 90,  # Consider 90%+ as completed
                'completion_percentage': min(100, max(0, completion_percentage)),
                'time_spent_seconds': time_spent,
                'last_accessed': timezone.now(),
                'feedback': data.get('feedback', {})
            }
        )
        
        # Update user's learning profile
        engine = AdaptiveLearningEngine(request.user)
        engine.update_learning_profile()
        
        # Get next recommended lessons
        recommended_lessons = engine.get_recommended_lessons(limit=3)
        
        return Response({
            'status': 'success',
            'message': 'Lesson progress updated',
            'progress': {
                'lesson_id': lesson.id,
                'completion_percentage': progress.completion_percentage,
                'is_completed': progress.is_completed,
                'time_spent_seconds': progress.time_spent_seconds
            },
            'next_recommendations': [{
                'id': l.id,
                'title': l.title,
                'difficulty': l.difficulty,
                'content_type': l.content_type
            } for l in recommended_lessons]
        })
        
    except Exception as e:
        logger.error(f"Error tracking lesson completion: {str(e)}", exc_info=True)
        return Response(
            {'error': 'Failed to track lesson completion'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

class AssessmentView(APIView):
    """
    API endpoint for handling assessments and adaptive testing.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, assessment_id=None):
        """
        Get an assessment for the user.
        
        If assessment_id is provided, returns that specific assessment.
        Otherwise, finds the most appropriate assessment for the user.
        
        Query Parameters:
            assessment_id (int, optional): Specific assessment ID to retrieve
            
        Returns:
            Response: JSON response with assessment details
        """
        try:
            user = request.user
            
            if assessment_id:
                # Get the specific assessment
                try:
                    assessment = Assessment.objects.get(
                        id=assessment_id,
                        is_active=True
                    )
                except Assessment.DoesNotExist:
                    return Response(
                        {'status': 'error', 'message': 'Assessment not found or inactive'},
                        status=status.HTTP_404_NOT_FOUND
                    )
            else:
                # Find the most appropriate assessment for the user
                # This is a simplified example - in a real app, you'd use more sophisticated logic
                # to determine the best assessment based on the user's level, progress, etc.
                
                # Get the user's last completed assessment to determine the next one
                last_attempt = AssessmentAttempt.objects.filter(
                    user=user,
                    is_completed=True
                ).order_by('-completed_at').first()
                
                if last_attempt and last_attempt.assessment.next_assessment:
                    # If there's a next assessment in sequence, use that
                    assessment = last_attempt.assessment.next_assessment
                else:
                    # Otherwise, find the first assessment the user hasn't completed yet
                    completed_assessments = AssessmentAttempt.objects.filter(
                        user=user,
                        is_completed=True
                    ).values_list('assessment_id', flat=True)
                    
                    assessment = Assessment.objects.filter(
                        is_active=True
                    ).exclude(
                        id__in=completed_assessments
                    ).order_by('order', 'id').first()
                    
                    if not assessment:
                        # If all assessments are completed, get the most recent one
                        assessment = Assessment.objects.filter(
                            is_active=True
                        ).order_by('-order', '-id').first()
            
            if not assessment:
                return Response(
                    {'status': 'error', 'message': 'No assessments available'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Check if there's an in-progress attempt
            attempt = AssessmentAttempt.objects.filter(
                user=user,
                assessment=assessment,
                is_completed=False
            ).first()
            
            if not attempt:
                # Create a new attempt
                attempt = AssessmentAttempt.objects.create(
                    user=user,
                    assessment=assessment,
                    started_at=timezone.now()
                )
            
            # Get the next question for the user
            answered_question_ids = UserResponse.objects.filter(
                attempt=attempt
            ).values_list('question_id', flat=True)
            
            next_question = Question.objects.filter(
                assessment=assessment,
                is_active=True
            ).exclude(
                id__in=answered_question_ids
            ).order_by('order').first()
            
            if not next_question:
                # If no more questions, mark as completed
                attempt.is_completed = True
                attempt.completed_at = timezone.now()
                attempt.save()
                
                # Calculate score
                correct_answers = UserResponse.objects.filter(
                    attempt=attempt,
                    is_correct=True
                ).count()
                
                total_questions = UserResponse.objects.filter(
                    attempt=attempt
                ).count()
                
                attempt.score = (correct_answers / total_questions * 100) if total_questions > 0 else 0
                attempt.save()
                
                # Update learning profile based on assessment results
                self._update_learning_profile(user, attempt)
                
                return Response({
                    'status': 'completed',
                    'message': 'Assessment completed',
                    'data': {
                        'assessment_id': assessment.id,
                        'title': assessment.title,
                        'score': attempt.score,
                        'completed_at': attempt.completed_at.isoformat(),
                        'correct_answers': correct_answers,
                        'total_questions': total_questions
                    }
                })
            
            # Serialize the question
            question_data = {
                'id': next_question.id,
                'text': next_question.text,
                'type': next_question.type,
                'order': next_question.order,
                'options': next_question.options if hasattr(next_question, 'options') else []
            }
            
            # Prepare the response
            response_data = {
                'status': 'in_progress',
                'data': {
                    'assessment': {
                        'id': assessment.id,
                        'title': assessment.title,
                        'description': assessment.description,
                        'time_limit_minutes': assessment.time_limit_minutes,
                        'passing_score': assessment.passing_score,
                        'question_count': assessment.questions.count()
                    },
                    'attempt_id': attempt.id,
                    'current_question': question_data,
                    'progress': {
                        'answered': len(answered_question_ids),
                        'total': assessment.questions.count(),
                        'percentage': int((len(answered_question_ids) / assessment.questions.count()) * 100) if assessment.questions.count() > 0 else 0
                    },
                    'started_at': attempt.started_at.isoformat(),
                    'time_remaining_seconds': (
                        (attempt.started_at + timedelta(minutes=assessment.time_limit_minutes) - timezone.now()).total_seconds()
                    ) if assessment.time_limit_minutes else None
                }
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in AssessmentView GET: {str(e)}", exc_info=True)
            return Response(
                {'status': 'error', 'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _update_learning_profile(self, user, attempt):
        """
        Update the user's learning profile based on assessment results.
        
        Args:
            user: The user object
            attempt: The completed assessment attempt
        """
        try:
            profile, created = AdaptiveLearningProfile.objects.get_or_create(user=user)
            
            # Update difficulty level based on score
            if attempt.score >= 80:  # Scored 80% or higher
                # Increase difficulty
                if profile.difficulty_level == 'beginner':
                    profile.difficulty_level = 'intermediate'
                elif profile.difficulty_level == 'intermediate':
                    profile.difficulty_level = 'advanced'
            elif attempt.score < 50:  # Scored less than 50%
                # Decrease difficulty
                if profile.difficulty_level == 'advanced':
                    profile.difficulty_level = 'intermediate'
                elif profile.difficulty_level == 'intermediate':
                    profile.difficulty_level = 'beginner'
            
            profile.save()
            
        except Exception as e:
            logger.error(f"Error updating learning profile: {str(e)}", exc_info=True)
        if assessment_id:
            # Get specific assessment
            try:
                assessment = Assessment.objects.get(
                    id=assessment_id,
                    is_active=True
                )
            except Assessment.DoesNotExist:
                raise Http404("Assessment not found")
        else:
            # Find the most appropriate assessment
            engine = AdaptiveLearningEngine(request.user)
            
            # Get the most recent incomplete assessment or create a new one
            assessment = Assessment.objects.filter(
                is_active=True,
                is_adaptive=True,
                start_date__lte=timezone.now(),
                end_date__gte=timezone.now()
            ).exclude(
                attempts__user=request.user,
                attempts__is_completed=True
            ).first()
            
            if not assessment:
                # Create a new adaptive assessment
                assessment = self._create_adaptive_assessment(request.user)
        
        # Get questions for this user
        questions = assessment.get_questions_for_user(request.user)
        
        # Format response
        return Response({
            'assessment': {
                'id': assessment.id,
                'title': assessment.title,
                'description': assessment.description,
                'instructions': assessment.instructions,
                'time_limit': assessment.time_limit,
                'is_adaptive': assessment.is_adaptive,
                'questions': [{
                    'id': q.id,
                    'question_text': q.question_text,
                    'question_type': q.question_type,
                    'difficulty': q.difficulty,
                    'points': q.points,
                    'answers': [{
                        'id': a.id,
                        'answer_text': a.answer_text,
                        'order': a.order
                    } for a in q.answers.all()]
                } for q in questions]
            }
        })
        
    def _check_answer(self, question, user_answer):
        """
        Handle different types of question answers and check if the user's answer is correct.
        
        Args:
            question: The question object
            user_answer: The user's answer to check
            
        Returns:
            bool: True if the answer is correct, False otherwise
        """
        try:
            data = request.data
            assessment_id = data.get('assessment_id')
            responses = data.get('responses', [])
            
            # Get the assessment
            try:
                assessment = Assessment.objects.get(id=assessment_id, is_active=True)
            except Assessment.DoesNotExist:
                return Response(
                    {'error': 'Assessment not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Create a new assessment attempt
            attempt = AssessmentAttempt.objects.create(
                user=request.user,
                assessment=assessment,
                start_time=timezone.now() - timedelta(seconds=sum(r.get('time_taken', 0) for r in responses)),
                end_time=timezone.now(),
                is_completed=True
            )
            
            # Process each response
            total_score = 0
            max_score = 0
            
            for response_data in responses:
                question_id = response_data.get('question_id')
                try:
                    question = Question.objects.get(id=question_id, assessment=assessment)
                except Question.DoesNotExist:
                    continue
                
                # Create user response
                user_response = UserResponse.objects.create(
                    user=request.user,
                    assessment=assessment,
                    question=question,
                    text_response=response_data.get('text_response', ''),
                    time_taken=response_data.get('time_taken', 0),
                    attempt=attempt
                )
                
                # Add selected answers if any
                selected_answers = response_data.get('selected_answers', [])
                if selected_answers:
                    answers = Answer.objects.filter(
                        id__in=selected_answers,
                        question=question
                    )
                    user_response.selected_answers.set(answers)
                
                # Calculate score for this response
                user_response.calculate_score()
                total_score += user_response.points_earned
                max_score += question.points
            
            # Update attempt with final score
            attempt.score = (total_score / max_score * 100) if max_score > 0 else 0
            attempt.save()
            
            # Update user's learning profile
            engine = AdaptiveLearningEngine(request.user)
            engine.update_learning_profile()
            
            # Get recommendations based on performance
            recommendations = engine.get_recommended_lessons(limit=3)
            
            return Response({
                'status': 'success',
                'score': attempt.score,
                'passed': attempt.score >= assessment.passing_score,
                'feedback': {
                    'correct': total_score,
                    'total': max_score,
                    'percentage': attempt.score
                },
                'recommendations': [{
                    'id': lesson.id,
                    'title': lesson.title,
                    'difficulty': lesson.difficulty,
                    'content_type': lesson.content_type
                } for lesson in recommendations]
            })
            
        except Exception as e:
            logger.error(f"Error submitting assessment: {str(e)}", exc_info=True)
            return Response(
                {'error': 'Failed to submit assessment'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def _create_adaptive_assessment(self, user):
        """
        Create a new adaptive assessment for the user.
        """
        # This is a simplified example - in a real application, you would
        # implement more sophisticated adaptive logic here
        
        # Get user's difficulty level
        difficulty = 'medium'
        if user.learning_condition == 'DYSLEXIA':
            difficulty = 'easy'
        elif user.learning_condition == 'ADVANCED':
            difficulty = 'hard'
        
        # Create assessment
        assessment = Assessment.objects.create(
            title=f"Adaptive Assessment - {user.username}",
            description="Personalized adaptive assessment",
            is_adaptive=True,
            passing_score=70,
            created_by=user,
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=7)
        )
        
        # Add questions based on difficulty
        questions = Question.objects.filter(
            difficulty=difficulty,
            is_active=True
        ).order_by('?')[:10]  # Random 10 questions
        
        # In a real implementation, you would use more sophisticated logic
        # to select questions based on the user's knowledge gaps, etc.
        
        return assessment

@csrf_exempt
def text_to_speech_view(request):
    """Convert text to speech for dyslexia support"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            text = data.get('text')
            user = request.user
            
            # Convert text to speech with personalized settings
            audio = TextToSpeechConverter.convert(text, user)
            
            return JsonResponse({
                'audio_url': audio.url,
                'duration': audio.duration
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    return JsonResponse({'error': 'POST request required'}, status=status.HTTP_400_BAD_REQUEST)

class AdaptiveLearningView(APIView):
    """View for adaptive learning"""
    def get(self, request):
        """Get adaptive learning recommendations"""
        user = request.user
        if not user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
            
        adaptive_profile = get_object_or_404(AdaptiveLearningProfile, user=user)
        
        return Response({
            'learning_style': adaptive_profile.learning_style,
            'engagement_level': adaptive_profile.engagement_level,
            'preferred_pace': adaptive_profile.preferred_pace,
            'next_assessment_due': adaptive_profile.next_assessment_due
        })

    def post(self, request):
        """Update adaptive learning profile"""
        user = request.user
        if not user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
            
        try:
            data = request.data
            adaptive_profile = AdaptiveLearningProfile.objects.get_or_create(user=user)[0]
            
            if 'learning_style' in data:
                adaptive_profile.learning_style = data['learning_style']
            if 'engagement_level' in data:
                adaptive_profile.engagement_level = data['engagement_level']
            if 'preferred_pace' in data:
                adaptive_profile.preferred_pace = data['preferred_pace']
            
            adaptive_profile.save()
            
            return Response({
                'message': 'Adaptive profile updated successfully',
                'profile': {
                    'learning_style': adaptive_profile.learning_style,
                    'engagement_level': adaptive_profile.engagement_level,
                    'preferred_pace': adaptive_profile.preferred_pace
                }
            })
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

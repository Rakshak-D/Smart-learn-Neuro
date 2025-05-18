"""
Utility functions for the AI app.
"""
import logging
import random
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta

from django.db.models import Q, Count, Avg, F, ExpressionWrapper, FloatField, IntegerField, Sum
from django.utils import timezone
from django.conf import settings

from lessons.models import Lesson, Topic, LessonProgress
from assessments.models import Assessment, Question, AssessmentAttempt, UserResponse
from users.models import CustomUser

logger = logging.getLogger(__name__)


class LearningStyleAnalyzer:
    """
    Analyzes a user's learning style based on their interactions with the platform.
    """
    
    def __init__(self, user):
        self.user = user
    
    def analyze(self) -> Dict[str, float]:
        """
        Analyze the user's learning style based on their activity.
        
        Returns:
            dict: A dictionary with learning style scores (visual, auditory, reading/writing, kinesthetic).
        """
        # Default scores
        scores = {
            'visual': 0.0,
            'auditory': 0.0,
            'reading_writing': 0.0,
            'kinesthetic': 0.0
        }
        
        try:
            # Get user's lesson progress
            progress = LessonProgress.objects.filter(user=self.user).select_related('lesson')
            
            # Count interactions by content type
            content_type_counts = progress.values('lesson__content_type').annotate(
                count=Count('id'),
                total_time=Sum('time_spent_seconds')
            )
            
            # Calculate scores based on content type
            for item in content_type_counts:
                content_type = item['lesson__content_type']
                count = item['count'] or 0
                total_time = item['total_time'] or 0
                
                # Weight by both count and time spent
                weight = (count * 0.4) + (total_time / 3600 * 0.6)  # Convert seconds to hours
                
                if content_type == 'video':
                    scores['visual'] += weight * 0.7
                    scores['auditory'] += weight * 0.3
                elif content_type == 'audio':
                    scores['auditory'] += weight * 0.9
                elif content_type == 'text':
                    scores['reading_writing'] += weight * 0.8
                    scores['visual'] += weight * 0.2
                elif content_type == 'interactive':
                    scores['kinesthetic'] += weight * 0.8
                    scores['visual'] += weight * 0.2
            
            # Normalize scores to sum to 1.0
            total = sum(scores.values())
            if total > 0:
                scores = {k: v / total for k, v in scores.items()}
            
            return scores
            
        except Exception as e:
            logger.error(f"Error analyzing learning style: {str(e)}", exc_info=True)
            return scores


def get_learning_analytics(user_id: int) -> Dict[str, Any]:
    """
    Get comprehensive learning analytics for a user.
    
    Args:
        user_id: The ID of the user.
        
    Returns:
        dict: A dictionary containing learning analytics data.
    """
    try:
        user = CustomUser.objects.get(id=user_id)
        now = timezone.now()
        
        # Get time-based data (last 30 days)
        thirty_days_ago = now - timedelta(days=30)
        
        # Get lesson completion stats
        completed_lessons = LessonProgress.objects.filter(
            user=user,
            is_completed=True
        ).count()
        
        total_lessons = Lesson.objects.count()
        completion_rate = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
        
        # Get time spent learning
        total_learning_time = user.total_learning_time or 0
        
        # Get assessment performance
        attempts = AssessmentAttempt.objects.filter(
            user=user,
            is_completed=True
        ).aggregate(
            avg_score=Avg('score'),
            total_attempts=Count('id')
        )
        
        # Get recent activity
        recent_activity = LessonProgress.objects.filter(
            user=user,
            updated_at__gte=thirty_days_ago
        ).order_by('-updated_at').select_related('lesson')[:10]
        
        # Get topic performance
        topic_performance = LessonProgress.objects.filter(
            user=user
        ).values(
            'lesson__topic__name'
        ).annotate(
            avg_completion=Avg('completion_percentage'),
            total_lessons=Count('id')
        )
        
        # Prepare response
        return {
            'user_id': user_id,
            'completion_rate': round(completion_rate, 2),
            'total_learning_time': total_learning_time,
            'completed_lessons': completed_lessons,
            'total_lessons': total_lessons,
            'average_score': round(attempts['avg_score'] or 0, 2),
            'total_assessment_attempts': attempts['total_attempts'] or 0,
            'recent_activity': [
                {
                    'lesson_id': activity.lesson.id,
                    'lesson_title': activity.lesson.title,
                    'completion_percentage': activity.completion_percentage,
                    'last_accessed': activity.updated_at
                } for activity in recent_activity
            ],
            'topic_performance': [
                {
                    'topic': item['lesson__topic__name'],
                    'average_completion': round(item['avg_completion'] or 0, 2),
                    'lessons_completed': item['total_lessons']
                } for item in topic_performance
            ]
        }
        
    except CustomUser.DoesNotExist:
        logger.error(f"User with ID {user_id} does not exist")
        raise
    except Exception as e:
        logger.error(f"Error getting learning analytics: {str(e)}", exc_info=True)
        raise


def generate_adaptive_lesson_plan(user_id: int, topic_id: int = None) -> List[Dict[str, Any]]:
    """
    Generate an adaptive lesson plan for a user.
    
    Args:
        user_id: The ID of the user.
        topic_id: Optional topic ID to focus on.
        
    Returns:
        list: A list of lesson plan items with metadata.
    """
    try:
        user = CustomUser.objects.get(id=user_id)
        
        # Get user's learning style (simplified for this example)
        analyzer = LearningStyleAnalyzer(user)
        learning_style = analyzer.analyze()
        
        # Determine preferred content types based on learning style
        preferred_types = []
        if learning_style['visual'] > 0.3:
            preferred_types.append('video')
        if learning_style['auditory'] > 0.3:
            preferred_types.append('audio')
        if learning_style['reading_writing'] > 0.3:
            preferred_types.append('text')
        if learning_style['kinesthetic'] > 0.3:
            preferred_types.append('interactive')
        
        # If no strong preferences, use all types
        if not preferred_types:
            preferred_types = ['video', 'audio', 'text', 'interactive']
        
        # Get recommended lessons based on user's progress and preferences
        base_query = Lesson.objects.filter(
            is_published=True,
            content_type__in=preferred_types
        )
        
        if topic_id:
            base_query = base_query.filter(topic_id=topic_id)
        
        # Exclude completed lessons for now (could be made configurable)
        completed_lesson_ids = LessonProgress.objects.filter(
            user=user,
            is_completed=True
        ).values_list('lesson_id', flat=True)
        
        if completed_lesson_ids:
            base_query = base_query.exclude(id__in=completed_lesson_ids)
        
        # Order by difficulty and duration
        lessons = base_query.order_by('difficulty', 'duration')[:10]  # Limit to 10 lessons for now
        
        # Convert to lesson plan format
        lesson_plan = []
        for i, lesson in enumerate(lessons, 1):
            lesson_plan.append({
                'order': i,
                'type': 'lesson',
                'lesson_id': lesson.id,
                'title': lesson.title,
                'content_type': lesson.content_type,
                'duration': lesson.duration,
                'difficulty': lesson.difficulty,
                'topic': lesson.topic.name if lesson.topic else 'General',
                'description': f"Learn about {lesson.title}"
            })
            
            # Add a short break after every 2 lessons
            if i % 2 == 0 and i < len(lessons):
                lesson_plan.append({
                    'order': i + 0.5,
                    'type': 'break',
                    'title': 'Short Break',
                    'duration': 300,  # 5 minutes
                    'description': 'Take a short break before continuing.'
                })
        
        # Add a final assessment if there are enough lessons
        if len(lessons) >= 3:
            lesson_plan.append({
                'order': len(lessons) + 1,
                'type': 'assessment',
                'title': 'Knowledge Check',
                'description': 'Test your understanding of the material',
                'duration': 1800,  # 30 minutes
                'difficulty': 'medium'
            })
        
        return lesson_plan
        
    except CustomUser.DoesNotExist:
        logger.error(f"User with ID {user_id} does not exist")
        raise
    except Exception as e:
        logger.error(f"Error generating adaptive lesson plan: {str(e)}", exc_info=True)
        raise


def update_learning_profile(user_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update a user's learning profile with new preferences and settings.
    
    Args:
        user_id: The ID of the user.
        data: Dictionary containing profile updates.
        
    Returns:
        dict: Updated user profile data.
    """
    try:
        user = CustomUser.objects.get(id=user_id)
        
        # Update fields if they exist in the data
        updatable_fields = [
            'learning_style', 'difficulty_level', 'preferred_content_types',
            'font_size', 'line_spacing', 'theme', 'notifications_enabled'
        ]
        
        updates = {}
        for field in updatable_fields:
            if field in data:
                setattr(user, field, data[field])
                updates[field] = data[field]
        
        user.save()
        
        # Log the update
        logger.info(f"Updated learning profile for user {user_id}: {updates}")
        
        # Return the updated profile
        return {
            'user_id': user_id,
            'updated_fields': list(updates.keys()),
            'profile': {
                'learning_style': user.learning_style,
                'difficulty_level': user.difficulty_level,
                'preferred_content_types': user.preferred_content_types,
                'accessibility_settings': {
                    'font_size': user.font_size,
                    'line_spacing': user.line_spacing,
                    'theme': user.theme,
                    'notifications_enabled': user.notifications_enabled
                }
            }
        }
        
    except CustomUser.DoesNotExist:
        logger.error(f"User with ID {user_id} does not exist")
        raise
    except Exception as e:
        logger.error(f"Error updating learning profile: {str(e)}", exc_info=True)
        raise

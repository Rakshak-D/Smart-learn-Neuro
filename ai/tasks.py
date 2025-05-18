"""
Background tasks for the AI app.
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from django.utils import timezone
from celery import shared_task

from lessons.models import LessonProgress, Lesson
from assessments.models import AssessmentAttempt, UserResponse, Question
from users.models import CustomUser
from .utils import LearningStyleAnalyzer, get_learning_analytics, generate_adaptive_lesson_plan

logger = logging.getLogger(__name__)


@shared_task(name="update_learning_analytics")
def update_learning_analytics_task(user_id: int) -> Dict[str, Any]:
    """
    Background task to update and return learning analytics for a user.
    
    Args:
        user_id: The ID of the user.
        
    Returns:
        dict: Learning analytics data.
    """
    try:
        logger.info(f"Updating learning analytics for user {user_id}")
        return get_learning_analytics(user_id)
    except Exception as e:
        logger.error(f"Error in update_learning_analytics_task: {str(e)}", exc_info=True)
        raise


@shared_task(name="generate_lesson_plan")
def generate_lesson_plan_task(user_id: int, topic_id: int = None) -> List[Dict[str, Any]]:
    """
    Background task to generate a personalized lesson plan for a user.
    
    Args:
        user_id: The ID of the user.
        topic_id: Optional topic ID to focus on.
        
    Returns:
        list: Generated lesson plan.
    """
    try:
        logger.info(f"Generating lesson plan for user {user_id}, topic: {topic_id}")
        return generate_adaptive_lesson_plan(user_id, topic_id)
    except Exception as e:
        logger.error(f"Error in generate_lesson_plan_task: {str(e)}", exc_info=True)
        raise


@shared_task(name="analyze_learning_style")
def analyze_learning_style_task(user_id: int) -> Dict[str, float]:
    """
    Background task to analyze a user's learning style.
    
    Args:
        user_id: The ID of the user.
        
    Returns:
        dict: Learning style scores.
    """
    try:
        logger.info(f"Analyzing learning style for user {user_id}")
        user = CustomUser.objects.get(id=user_id)
        analyzer = LearningStyleAnalyzer(user)
        return analyzer.analyze()
    except CustomUser.DoesNotExist:
        logger.error(f"User with ID {user_id} does not exist")
        raise
    except Exception as e:
        logger.error(f"Error in analyze_learning_style_task: {str(e)}", exc_info=True)
        raise


@shared_task(name="generate_weekly_report")
def generate_weekly_report(user_id: int) -> Dict[str, Any]:
    """
    Generate a weekly learning report for a user.
    
    Args:
        user_id: The ID of the user.
        
    Returns:
        dict: Weekly learning report.
    """
    try:
        user = CustomUser.objects.get(id=user_id)
        one_week_ago = timezone.now() - timedelta(days=7)
        
        # Get completed lessons in the past week
        completed_lessons = LessonProgress.objects.filter(
            user=user,
            is_completed=True,
            updated_at__gte=one_week_ago
        ).select_related('lesson')
        
        # Get assessment attempts in the past week
        assessment_attempts = AssessmentAttempt.objects.filter(
            user=user,
            end_time__gte=one_week_ago,
            is_completed=True
        ).select_related('assessment')
        
        # Calculate time spent learning
        total_learning_time = sum(
            (lp.time_spent_seconds or 0) 
            for lp in completed_lessons
        )
        
        # Calculate average score
        avg_score = assessment_attempts.aggregate(avg=Avg('score'))['avg'] or 0
        
        # Get most active day
        activity_by_day = {}
        for day in range(7):
            date = (timezone.now() - timedelta(days=day)).date()
            activity = completed_lessons.filter(
                updated_at__date=date
            ).count()
            activity_by_day[date.strftime('%A')] = activity
        
        most_active_day = max(activity_by_day.items(), key=lambda x: x[1])[0] if activity_by_day else "No activity"
        
        # Generate report
        report = {
            'user_id': user_id,
            'report_period': {
                'start': one_week_ago.date(),
                'end': timezone.now().date()
            },
            'metrics': {
                'lessons_completed': completed_lessons.count(),
                'assessments_taken': assessment_attempts.count(),
                'total_learning_time_seconds': total_learning_time,
                'average_score': round(avg_score, 2),
                'most_active_day': most_active_day,
                'activity_by_day': activity_by_day
            },
            'recent_lessons': [
                {
                    'id': lesson.lesson.id,
                    'title': lesson.lesson.title,
                    'completed_at': lesson.updated_at.date(),
                    'time_spent_seconds': lesson.time_spent_seconds
                }
                for lesson in completed_lessons.order_by('-updated_at')[:5]  # Last 5 lessons
            ],
            'recommendations': generate_adaptive_lesson_plan(user_id)
        }
        
        # TODO: Send email with the report
        
        return report
        
    except CustomUser.DoesNotExist:
        logger.error(f"User with ID {user_id} does not exist")
        raise
    except Exception as e:
        logger.error(f"Error generating weekly report: {str(e)}", exc_info=True)
        raise


@shared_task(name="process_adaptive_assessment")
def process_adaptive_assessment(attempt_id: int) -> Dict[str, Any]:
    """
    Process an adaptive assessment attempt.
    
    Args:
        attempt_id: The ID of the assessment attempt.
        
    Returns:
        dict: Processing results.
    """
    try:
        attempt = AssessmentAttempt.objects.get(id=attempt_id)
        
        if not attempt.is_completed:
            logger.warning(f"Assessment attempt {attempt_id} is not marked as completed")
            return {'status': 'error', 'message': 'Assessment not completed'}
        
        # Get all responses for this attempt
        responses = UserResponse.objects.filter(attempt=attempt).select_related('question')
        
        # Calculate score
        total_questions = responses.count()
        if total_questions == 0:
            return {'status': 'error', 'message': 'No responses found'}
        
        correct_answers = responses.filter(is_correct=True).count()
        score = (correct_answers / total_questions) * 100
        
        # Update attempt with score
        attempt.score = score
        attempt.save()
        
        # Analyze performance by question difficulty
        difficulty_analysis = responses.values('question__difficulty').annotate(
            total=Count('id'),
            correct=Count('id', filter=Q(is_correct=True)),
            avg_time=Avg('time_taken')
        )
        
        # Generate feedback
        feedback = []
        for item in difficulty_analysis:
            difficulty = item['question__difficulty']
            accuracy = (item['correct'] / item['total']) * 100 if item['total'] > 0 else 0
            
            if accuracy < 50:
                feedback.append(
                    f"You struggled with {difficulty} questions (accuracy: {accuracy:.1f}%). "
                    f"Consider reviewing these topics."
                )
            else:
                feedback.append(
                    f"Good job on {difficulty} questions (accuracy: {accuracy:.1f}%)."
                )
        
        # Update user's learning profile if needed
        user = attempt.user
        if score < 50 and not user.difficulty_level == 'beginner':
            user.difficulty_level = 'beginner'
            user.save()
            feedback.append("Your difficulty level has been adjusted to 'beginner' based on your performance.")
        
        return {
            'status': 'success',
            'attempt_id': attempt_id,
            'score': score,
            'correct_answers': correct_answers,
            'total_questions': total_questions,
            'difficulty_analysis': list(difficulty_analysis),
            'feedback': feedback
        }
        
    except AssessmentAttempt.DoesNotExist:
        logger.error(f"Assessment attempt with ID {attempt_id} does not exist")
        return {'status': 'error', 'message': 'Assessment attempt not found'}
    except Exception as e:
        logger.error(f"Error processing adaptive assessment: {str(e)}", exc_info=True)
        return {'status': 'error', 'message': str(e)}

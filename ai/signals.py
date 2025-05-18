"""
Signals for the AI app.
"""
import logging
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

from django.apps import apps

# Get models using string references to avoid circular imports
CustomUser = apps.get_model('users', 'CustomUser')
LessonProgress = apps.get_model('lessons', 'LessonProgress')
AssessmentAttempt = apps.get_model('assessments', 'AssessmentAttempt')

logger = logging.getLogger(__name__)


@receiver(post_save, sender=LessonProgress)
def update_learning_metrics(sender, instance, created, **kwargs):
    """
    Update user's learning metrics when a lesson progress is saved.
    """
    try:
        user = instance.user
        
        # Update total learning time
        if instance.time_spent_seconds:
            user.total_learning_time = (user.total_learning_time or 0) + instance.time_spent_seconds
        
        # Update learning streak if the lesson was completed today
        if instance.is_completed and instance.completion_date.date() == timezone.now().date():
            last_activity = user.last_learning_activity
            
            # If last activity was yesterday or today, increment streak
            if last_activity and (timezone.now().date() - last_activity.date()).days <= 1:
                user.learning_streak = (user.learning_streak or 0) + 1
            else:
                # Reset streak if there was a gap
                user.learning_streak = 1
                
            user.last_learning_activity = timezone.now()
        
        user.save()
        
    except Exception as e:
        logger.error(f"Error updating learning metrics: {str(e)}", exc_info=True)


@receiver(post_save, sender=AssessmentAttempt)
def update_assessment_metrics(sender, instance, created, **kwargs):
    """
    Update user's assessment metrics when an assessment attempt is saved.
    """
    try:
        if not instance.is_completed:
            return
            
        user = instance.user
        
        # Update assessment count
        user.assessment_count = (user.assessment_count or 0) + 1
        
        # Update average score
        if instance.score is not None:
            total_score = (user.average_assessment_score or 0) * ((user.assessment_count or 1) - 1)
            user.average_assessment_score = (total_score + instance.score) / user.assessment_count
        
        user.save()
        
    except Exception as e:
        logger.error(f"Error updating assessment metrics: {str(e)}", exc_info=True)


@receiver(pre_save, sender=CustomUser)
def set_default_learning_preferences(sender, instance, **kwargs):
    """
    Set default learning preferences for new users based on their learning condition.
    """
    if not instance.pk:  # Only for new users
        if not hasattr(instance, 'learning_condition'):
            instance.learning_condition = 'NORMAL'  # Default learning condition
            
        # Set default preferences based on learning condition
        if instance.learning_condition == 'DYSLEXIA':
            instance.font_size = 'large'
            instance.line_spacing = 1.5
            instance.preferred_content_types = ['audio', 'video']
            instance.difficulty_level = 'beginner'
            
        elif instance.learning_condition == 'ADHD':
            instance.font_size = 'medium'
            instance.line_spacing = 1.2
            instance.preferred_content_types = ['interactive', 'video']
            instance.difficulty_level = 'beginner'
            
        else:  # NORMAL or other conditions
            instance.font_size = 'medium'
            instance.line_spacing = 1.0
            instance.preferred_content_types = ['text', 'video', 'interactive']
            instance.difficulty_level = 'beginner'

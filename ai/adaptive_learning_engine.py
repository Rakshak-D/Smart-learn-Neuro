"""
Adaptive Learning Engine for SmartLearn Neuro

This module implements the core adaptive learning algorithms that power the
personalized learning experience for students with different learning needs.
"""
import logging
from typing import Dict, List, Optional, Tuple
import numpy as np
from django.utils import timezone
from datetime import timedelta
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from users.models import CustomUser
from lessons.models import Lesson, Topic, LessonProgress
from assessments.models import Assessment, AssessmentAttempt, Question, UserResponse

logger = logging.getLogger(__name__)

class AdaptiveLearningEngine:
    """
    Core adaptive learning engine that personalizes the learning experience
    based on user behavior, performance, and preferences.
    """
    
    def __init__(self, user: CustomUser):
        """Initialize the adaptive learning engine for a specific user."""
        self.user = user
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
    def get_recommended_lessons(self, limit: int = 5) -> List[Lesson]:
        """
        Get recommended lessons for the user based on their learning profile.
        
        Args:
            limit: Maximum number of lessons to return
            
        Returns:
            List of recommended Lesson objects
        """
        # Get user's completed lessons
        completed_lessons = set(self.user.completed_lessons.all())
        
        # Get topics the user has shown interest in
        interested_topics = self._get_interested_topics()
        
        # Get lessons that match user's current level and interests
        recommended = []
        
        # 1. Recommend lessons from topics the user is interested in
        for topic in interested_topics:
            lessons = (
                Lesson.objects
                .filter(topic=topic, is_published=True)
                .exclude(id__in=[l.id for l in completed_lessons])
                .order_by('difficulty')
            )
            
            # Add lessons that match user's current difficulty level
            for lesson in lessons:
                if self._is_appropriate_difficulty(lesson):
                    recommended.append(lesson)
                    if len(recommended) >= limit:
                        return recommended
        
        # 2. If not enough recommendations, suggest lessons from related topics
        if len(recommended) < limit:
            related_lessons = (
                Lesson.objects
                .filter(is_published=True)
                .exclude(id__in=[l.id for l in completed_lessons])
                .order_by('?')  # Random order for variety
            )
            
            for lesson in related_lessons:
                if self._is_appropriate_difficulty(lesson):
                    recommended.append(lesson)
                    if len(recommended) >= limit:
                        break
        
        return recommended
    
    def _get_interested_topics(self) -> List[Topic]:
        """
        Get topics the user has shown interest in based on their activity.
        """
        # Get topics from completed lessons
        completed_topics = set()
        for lesson in self.user.completed_lessons.all():
            if lesson.topic:
                completed_topics.add(lesson.topic)
        
        # If no completed lessons, return some default topics
        if not completed_topics:
            return list(Topic.objects.filter(is_active=True).order_by('?')[:3])
        
        # Otherwise, find related topics
        related_topics = set()
        for topic in completed_topics:
            # Find topics with the same subject
            related = Topic.objects.filter(
                subject=topic.subject,
                is_active=True
            ).exclude(id__in=[t.id for t in completed_topics])
            related_topics.update(related)
        
        return list(completed_topics) + list(related_topics)[:5]
    
    def _is_appropriate_difficulty(self, lesson: Lesson) -> bool:
        """
        Check if a lesson's difficulty is appropriate for the user.
        """
        # Map difficulty levels to numeric values
        difficulty_map = {
            'beginner': 1,
            'intermediate': 2,
            'advanced': 3
        }
        
        # Get user's current level
        user_level = difficulty_map.get(self.user.difficulty_level.lower(), 1)
        
        # Get lesson difficulty
        lesson_level = difficulty_map.get(lesson.difficulty.lower(), 1)
        
        # Consider the lesson appropriate if it's at or slightly above the user's level
        return abs(lesson_level - user_level) <= 1
    
    def update_learning_profile(self) -> Dict:
        """
        Update the user's learning profile based on recent activity.
        
        Returns:
            Dict containing the updated profile data
        """
        updates = {}
        
        # Update difficulty level based on assessment performance
        self._update_difficulty_level(updates)
        
        # Update learning preferences based on interaction patterns
        self._update_learning_preferences(updates)
        
        # Update engagement metrics
        self._update_engagement_metrics(updates)
        
        # Save updates to the user model
        if updates:
            for key, value in updates.items():
                setattr(self.user, key, value)
            self.user.save()
        
        return updates
    
    def _update_difficulty_level(self, updates: Dict) -> None:
        """Update user's difficulty level based on assessment performance."""
        # Get recent assessment attempts
        recent_attempts = (
            AssessmentAttempt.objects
            .filter(user=self.user, is_completed=True)
            .order_by('-end_time')[:5]  # Last 5 attempts
        )
        
        if not recent_attempts:
            return
        
        # Calculate average score
        avg_score = sum(attempt.score or 0 for attempt in recent_attempts) / len(recent_attempts)
        
        # Update difficulty level based on performance
        difficulty_levels = ['beginner', 'intermediate', 'advanced']
        current_level = self.user.difficulty_level.lower()
        current_index = difficulty_levels.index(current_level) if current_level in difficulty_levels else 0
        
        if avg_score > 80 and current_index < len(difficulty_levels) - 1:
            # Increase difficulty if consistently scoring high
            updates['difficulty_level'] = difficulty_levels[current_index + 1]
        elif avg_score < 50 and current_index > 0:
            # Decrease difficulty if struggling
            updates['difficulty_level'] = difficulty_levels[current_index - 1]
    
    def _update_learning_preferences(self, updates: Dict) -> None:
        """Update user's learning preferences based on interaction patterns."""
        # Get recent lesson interactions
        recent_lessons = (
            LessonProgress.objects
            .filter(user=self.user, is_completed=True)
            .order_by('-completion_date')[:10]  # Last 10 completed lessons
        )
        
        if not recent_lessons:
            return
        
        # Track preferred content types
        content_preferences = {
            'video': 0,
            'audio': 0,
            'text': 0,
            'interactive': 0
        }
        
        for progress in recent_lessons:
            if progress.lesson.content_type in content_preferences:
                content_preferences[progress.lesson.content_type] += 1
        
        # Update preferences based on most common content types
        preferred_content = max(content_preferences.items(), key=lambda x: x[1])
        
        if preferred_content[1] > 0:  # If we have data
            updates.update({
                'prefers_video': preferred_content[0] == 'video',
                'prefers_audio': preferred_content[0] == 'audio',
                'prefers_text': preferred_content[0] == 'text',
            })
    
    def _update_engagement_metrics(self, updates: Dict) -> None:
        """Update user engagement metrics."""
        # Calculate engagement score based on recent activity
        last_week = timezone.now() - timedelta(days=7)
        
        # Count active days in the last week
        active_days = (
            LessonProgress.objects
            .filter(user=self.user, completion_date__gte=last_week)
            .values_list('completion_date__date', flat=True)
            .distinct()
            .count()
        )
        
        # Update engagement level (0-1 scale)
        engagement = min(1.0, active_days / 7.0)
        updates['engagement_level'] = engagement
        
        # Update learning streak
        if active_days > 0:
            updates['learning_streak'] = (self.user.learning_streak or 0) + 1
        else:
            updates['learning_streak'] = 0
    
    def generate_learning_path(self) -> List[Dict]:
        """
        Generate a personalized learning path for the user.
        
        Returns:
            List of dictionaries representing the learning path steps
        """
        learning_path = []
        
        # Get user's current level and learning condition
        user_level = self.user.difficulty_level.lower()
        learning_condition = self.user.learning_condition
        
        # Define learning path templates based on user's condition
        if learning_condition == 'DYSLEXIA':
            # For dyslexic learners, focus on multi-sensory approaches
            learning_path.extend([
                self._create_learning_step('Introduction to Topic', 'video'),
                self._create_learning_step('Interactive Exercise', 'interactive'),
                self._create_learning_step('Audio Summary', 'audio'),
                self._create_learning_step('Practice Quiz', 'assessment'),
            ])
        elif learning_condition == 'ADHD':
            # For ADHD, use shorter, more engaging content with breaks
            learning_path.extend([
                self._create_learning_step('Quick Video Intro', 'video', duration=5),
                self._create_learning_step('Short Interactive Activity', 'interactive', duration=10),
                self._create_learning_step('Movement Break', 'break', duration=2),
                self._create_learning_step('Practice Questions', 'assessment', duration=15),
            ])
        else:
            # Standard learning path
            learning_path.extend([
                self._create_learning_step('Learn the Basics', 'video'),
                self._create_learning_step('Read and Review', 'text'),
                self._create_learning_step('Practice Exercises', 'interactive'),
                self._create_learning_step('Assessment', 'assessment'),
            ])
        
        # Add personalized recommendations
        recommended_lessons = self.get_recommended_lessons(limit=3)
        if recommended_lessons:
            learning_path.append({
                'type': 'recommendation',
                'title': 'Recommended for You',
                'description': 'Lessons tailored to your interests and progress',
                'items': [
                    {
                        'id': lesson.id,
                        'title': lesson.title,
                        'description': lesson.description[:100] + '...' if lesson.description else '',
                        'difficulty': lesson.difficulty,
                        'duration': lesson.duration or 10,
                        'content_type': lesson.content_type
                    }
                    for lesson in recommended_lessons
                ]
            })
        
        return learning_path
    
    def _create_learning_step(self, title: str, step_type: str, duration: int = None) -> Dict:
        """Helper method to create a learning path step."""
        return {
            'type': step_type,
            'title': title,
            'duration': duration or 10,  # Default 10 minutes
            'status': 'pending',
            'completed': False
        }
    
    def get_learning_analytics(self) -> Dict:
        """
        Get learning analytics for the user.
        
        Returns:
            Dict containing learning analytics data
        """
        # Calculate time spent learning
        total_learning_time = self.user.total_learning_time or 0
        
        # Get completion stats
        completed_lessons = self.user.completed_lessons.count()
        total_lessons = Lesson.objects.filter(is_published=True).count()
        completion_rate = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
        
        # Get performance metrics
        attempts = AssessmentAttempt.objects.filter(user=self.user, is_completed=True)
        avg_score = attempts.aggregate(avg_score=models.Avg('score'))['avg_score'] or 0
        
        # Get activity timeline (last 7 days)
        today = timezone.now().date()
        week_ago = today - timedelta(days=6)
        
        # Generate date range for the last 7 days
        date_range = [today - timedelta(days=i) for i in range(6, -1, -1)]
        
        # Get daily activity counts
        daily_activity = (
            LessonProgress.objects
            .filter(
                user=self.user,
                completion_date__date__gte=week_ago,
                completion_date__date__lte=today
            )
            .annotate(date=models.functions.TruncDate('completion_date'))
            .values('date')
            .annotate(count=models.Count('id'))
            .order_by('date')
        )
        
        # Convert to a dictionary for easier lookup
        activity_dict = {item['date']: item['count'] for item in daily_activity}
        
        # Create activity data for each day in the range
        activity_data = [{
            'date': date.strftime('%Y-%m-%d'),
            'count': activity_dict.get(date, 0)
        } for date in date_range]
        
        return {
            'total_learning_time': total_learning_time,
            'completion_rate': round(completion_rate, 1),
            'lessons_completed': completed_lessons,
            'total_lessons': total_lessons,
            'average_score': round(avg_score, 1) if avg_score else None,
            'learning_streak': self.user.learning_streak or 0,
            'activity_data': activity_data,
            'preferred_learning_style': self._get_preferred_learning_style(),
            'next_recommendations': self.get_recommended_lessons(limit=3)
        }
    
    def _get_preferred_learning_style(self) -> str:
        """Determine the user's preferred learning style based on activity."""
        # Get user's most common interaction types
        interaction_types = (
            LessonProgress.objects
            .filter(user=self.user)
            .values('lesson__content_type')
            .annotate(count=models.Count('id'))
            .order_by('-count')
        )
        
        if interaction_types:
            return interaction_types[0].get('lesson__content_type', 'text')
        return 'text'

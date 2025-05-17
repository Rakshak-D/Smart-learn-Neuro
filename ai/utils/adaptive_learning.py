from django.conf import settings
import numpy as np
from sklearn.preprocessing import StandardScaler
from datetime import datetime, timedelta
import json

class AdaptiveLearningEngine:
    def __init__(self, user):
        self.user = user
        self.scaler = StandardScaler()
        
    def get_personalized_lessons(self):
        """Get personalized lessons based on user's learning style and performance"""
        # Get user's learning profile
        profile = self._get_learning_profile()
        
        # Get recommended lessons based on profile
        lessons = self._recommend_lessons(profile)
        
        return lessons
    
    def _get_learning_profile(self):
        """Get user's learning profile"""
        profile = {
            'learning_style': self.user.learning_style,
            'engagement_level': self.user.engagement_level,
            'preferred_pace': self.user.preferred_pace,
            'learning_condition': self.user.learning_condition,
            'recent_performance': self._get_recent_performance(),
            'preferred_format': self._get_preferred_format()
        }
        return profile
    
    def _get_recent_performance(self):
        """Get user's recent performance metrics"""
        # Get recent assessment results
        recent_results = AssessmentResult.objects.filter(
            user=self.user,
            completed_at__gte=datetime.now() - timedelta(days=7)
        ).order_by('-completed_at')[:5]
        
        # Calculate performance metrics
        scores = [r.score for r in recent_results]
        if scores:
            return {
                'average_score': np.mean(scores),
                'score_std': np.std(scores),
                'last_score': scores[0]
            }
        return {'average_score': 0, 'score_std': 0, 'last_score': 0}
    
    def _get_preferred_format(self):
        """Determine user's preferred learning format"""
        if self.user.prefers_audio:
            return 'audio'
        elif self.user.prefers_chunked:
            return 'chunked_text'
        return 'standard_text'
    
    def _recommend_lessons(self, profile):
        """Recommend lessons based on learning profile"""
        # Get all available lessons
        from lessons.models import Lesson
        lessons = Lesson.objects.filter(subject='English')
        
        # Filter lessons based on user's learning condition
        if profile['learning_condition'] == 'DYSLEXIA':
            lessons = lessons.filter(
                Q(dyslexia_friendly=True) |
                Q(interactive_elements=True)
            )
        elif profile['learning_condition'] == 'ADHD':
            lessons = lessons.filter(
                Q(interactive_elements=True) |
                Q(short_duration=True)
            )
        
        # Sort lessons by relevance
        sorted_lessons = sorted(
            lessons,
            key=lambda l: self._calculate_relevance_score(l, profile),
            reverse=True
        )
        
        return [self._format_lesson(l) for l in sorted_lessons[:5]]
    
    def _calculate_relevance_score(self, lesson, profile):
        """Calculate relevance score for a lesson"""
        score = 0
        
        # Weight factors based on user's learning style
        weights = {
            'difficulty': 0.3,
            'format': 0.2,
            'engagement': 0.3,
            'recent_performance': 0.2
        }
        
        # Calculate difficulty score
        difficulty_score = self._calculate_difficulty_score(lesson, profile)
        score += weights['difficulty'] * difficulty_score
        
        # Calculate format score
        format_score = self._calculate_format_score(lesson, profile)
        score += weights['format'] * format_score
        
        # Calculate engagement score
        engagement_score = self._calculate_engagement_score(lesson, profile)
        score += weights['engagement'] * engagement_score
        
        # Calculate performance score
        performance_score = self._calculate_performance_score(lesson, profile)
        score += weights['performance'] * performance_score
        
        return score
    
    def _calculate_difficulty_score(self, lesson, profile):
        """Calculate difficulty score based on user's performance"""
        if profile['recent_performance']['average_score'] > 80:
            return 1 if lesson.difficulty == 'advanced' else 0.5
        elif profile['recent_performance']['average_score'] > 60:
            return 1 if lesson.difficulty == 'intermediate' else 0.5
        else:
            return 1 if lesson.difficulty == 'beginner' else 0.5
    
    def _calculate_format_score(self, lesson, profile):
        """Calculate score based on preferred format"""
        if profile['preferred_format'] == 'audio' and lesson.has_audio:
            return 1
        elif profile['preferred_format'] == 'chunked_text' and lesson.chunked_content:
            return 1
        return 0.5
    
    def _calculate_engagement_score(self, lesson, profile):
        """Calculate engagement score based on user's engagement level"""
        if profile['engagement_level'] > 0.8 and lesson.interactive_elements:
            return 1
        elif profile['engagement_level'] > 0.5 and lesson.has_media:
            return 0.8
        return 0.5
    
    def _calculate_performance_score(self, lesson, profile):
        """Calculate score based on recent performance"""
        if profile['recent_performance']['last_score'] > 80 and lesson.advanced_topics:
            return 1
        elif profile['recent_performance']['last_score'] > 60 and lesson.intermediate_topics:
            return 0.8
        return 0.5
    
    def _format_lesson(self, lesson):
        """Format lesson data for API response"""
        return {
            'id': lesson.id,
            'title': lesson.title,
            'description': lesson.description,
            'difficulty': lesson.difficulty,
            'duration': lesson.duration,
            'format': lesson.format,
            'recommended': True
        }

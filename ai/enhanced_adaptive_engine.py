"""
Enhanced Adaptive Learning Engine with Advanced Features
"""
import logging
import numpy as np
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import json

import tensorflow as tf
from tensorflow.keras.models import load_model
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import spacy

from django.conf import settings
from django.utils import timezone
from users.models import CustomUser
from lessons.models import Lesson, Topic, LessonProgress
from assessments.models import Assessment, AssessmentAttempt, Question

logger = logging.getLogger(__name__)

class EnhancedAdaptiveEngine:
    """Enhanced adaptive learning engine with advanced ML capabilities."""
    
    def __init__(self, user: CustomUser):
        self.user = user
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.nlp = spacy.load('en_core_web_sm')
        self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
        self._load_models()
    
    def _load_models(self):
        """Load pre-trained models."""
        try:
            # Load recommendation model
            self.recommendation_model = self._load_recommendation_model()
            # Load engagement prediction model
            self.engagement_model = self._load_engagement_model()
        except Exception as e:
            self.logger.error(f"Error loading models: {e}")
            raise
    
    def _load_recommendation_model(self):
        """Load the recommendation model."""
        try:
            # Try to load a pre-trained model if it exists
            model_path = getattr(settings, 'RECOMMENDATION_MODEL_PATH', None)
            if model_path:
                return load_model(model_path)
            return None
        except Exception as e:
            self.logger.warning(f"Could not load recommendation model: {e}")
            return None
    
    def _load_engagement_model(self):
        """Load the engagement prediction model."""
        try:
            # Try to load a pre-trained model if it exists
            model_path = getattr(settings, 'ENGAGEMENT_MODEL_PATH', None)
            if model_path:
                return load_model(model_path)
            return None
        except Exception as e:
            self.logger.warning(f"Could not load engagement model: {e}")
            return None
    
    def get_personalized_lessons(self, limit: int = 5) -> List[Dict]:
        """
        Get personalized lesson recommendations.
        
        Args:
            limit: Maximum number of recommendations to return
            
        Returns:
            List of recommended lessons with metadata
        """
        try:
            # Get user's learning profile and history
            profile = self._get_user_profile()
            history = self._get_learning_history()
            
            # Generate recommendations
            recommendations = self._generate_recommendations(profile, history, limit)
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {e}")
            # Fallback to basic recommendations
            return self._get_fallback_recommendations(limit)
    
    def analyze_engagement(self, video_frame=None, interaction_data=None):
        """
        Analyze user engagement from video and interaction data.
        
        Args:
            video_frame: Optional video frame for visual analysis
            interaction_data: Interaction metrics (clicks, scrolls, etc.)
            
        Returns:
            Engagement score and analysis
        """
        try:
            features = self._extract_engagement_features(video_frame, interaction_data)
            
            if self.engagement_model:
                # Use ML model for prediction
                engagement_score = self.engagement_model.predict([features])[0][0]
            else:
                # Fallback to rule-based scoring
                engagement_score = self._calculate_engagement_score(features)
                
            return {
                'score': float(engagement_score),
                'level': self._get_engagement_level(engagement_score),
                'features': features,
                'timestamp': timezone.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error in engagement analysis: {e}")
            return {
                'score': 0.5,
                'level': 'neutral',
                'error': str(e),
                'timestamp': timezone.now().isoformat()
            }
    
    def _extract_engagement_features(self, video_frame, interaction_data):
        """Extract features for engagement analysis."""
        features = {}
        
        # Extract visual features if video frame is provided
        if video_frame is not None:
            try:
                # Use OpenCV for face detection and analysis
                import cv2
                gray = cv2.cvtColor(video_frame, cv2.COLOR_BGR2GRAY)
                face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                faces = face_cascade.detectMultiScale(gray, 1.1, 4)
                
                if len(faces) > 0:
                    features['face_detected'] = 1
                    features['face_count'] = len(faces)
                    # Add more face analysis features here
                else:
                    features['face_detected'] = 0
                    features['face_count'] = 0
            except Exception as e:
                self.logger.warning(f"Error in face detection: {e}")
        
        # Add interaction features
        if interaction_data:
            features.update({
                'clicks': interaction_data.get('clicks', 0),
                'scrolls': interaction_data.get('scrolls', 0),
                'active_time': interaction_data.get('active_time', 0),
                'idle_time': interaction_data.get('idle_time', 0)
            })
        
        return features
    
    def _generate_recommendations(self, profile, history, limit):
        """Generate personalized recommendations."""
        # This is a simplified example - in practice, you would use collaborative filtering,
        # content-based filtering, or hybrid approaches
        
        # Get all available lessons
        all_lessons = list(Lesson.objects.all())
        
        # Score each lesson based on user profile and history
        scored_lessons = []
        for lesson in all_lessons:
            score = self._score_lesson(lesson, profile, history)
            scored_lessons.append((lesson, score))
        
        # Sort by score and return top N
        scored_lessons.sort(key=lambda x: x[1], reverse=True)
        
        return [{
            'id': lesson.id,
            'title': lesson.title,
            'topic': lesson.topic.name,
            'difficulty': lesson.difficulty,
            'score': score,
            'url': lesson.get_absolute_url()
        } for lesson, score in scored_lessons[:limit]]
    
    def _score_lesson(self, lesson, profile, history):
        """Score a lesson for recommendation."""
        score = 0.0
        
        # Add base score based on topic relevance
        topic_relevance = self._calculate_topic_relevance(lesson.topic, profile)
        score += topic_relevance * 0.4
        
        # Adjust based on difficulty
        difficulty_score = self._calculate_difficulty_match(lesson.difficulty, profile)
        score += difficulty_score * 0.3
        
        # Adjust based on past interactions
        interaction_score = self._calculate_interaction_score(lesson, history)
        score += interaction_score * 0.3
        
        return min(max(score, 0.0), 1.0)
    
    def _get_user_profile(self):
        """Get user profile data."""
        return {
            'learning_style': self.user.learning_style,
            'preferred_modality': self.user.preferred_modality,
            'difficulty_level': self.user.difficulty_level,
            'interests': list(self.user.interests.values_list('name', flat=True)),
            'accessibility_needs': self.user.accessibility_needs
        }
    
    def _get_learning_history(self):
        """Get user's learning history."""
        return {
            'completed_lessons': list(self.user.completed_lessons.values_list('id', flat=True)),
            'in_progress': list(self.user.lessonprogress_set.filter(completed=False).values('lesson_id', 'progress')),
            'assessment_scores': list(self.user.assessment_attempts.values('assessment_id', 'score')),
            'recent_activity': list(self.user.activity_logs.order_by('-timestamp').values('action', 'timestamp')[:10])
        }
    
    def _get_fallback_recommendations(self, limit):
        """Get fallback recommendations if ML models fail."""
        return list(Lesson.objects.order_by('?')[:limit].values('id', 'title', 'topic__name'))
    
    def _get_engagement_level(self, score):
        """Convert engagement score to level."""
        if score >= 0.8:
            return 'high'
        elif score >= 0.5:
            return 'medium'
        else:
            return 'low'

"""
URL configuration for AI services in SmartLearn Neuro.

This module defines all the API endpoints for AI services including text analysis,
speech processing, computer vision, and adaptive learning features.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.documentation import include_docs_urls
from rest_framework.schemas import get_schema_view
from rest_framework_simplejwt.views import TokenRefreshView

from . import views
from .api_views import (
    TextSimilarityView,
    KeywordExtractionView,
    SentimentAnalysisView,
    EngagementAnalysisView,
    AdaptiveLearningView,
    TextToSpeechView,
    HealthCheckView,
)

# Import existing views
from .views import (
    SpeechToTextView,
    FaceDetectionView,
    GestureRecognitionView,
    ContentModerationView,
    LearningPathView,
    LearningAnalyticsView,
    LessonRecommendationView,
    UpdateLearningProfileView,
    track_lesson_completion,
    AssessmentView,
    EngagementAnalyticsView,
    PerformanceAnalyticsView,
    CompletionAnalyticsView,
)

# API Router
router = DefaultRouter()

# ===== API Endpoint Groups =====

# Text Analysis Endpoints
text_analysis_patterns = [
    path('similarity/', TextSimilarityView.as_view(), name='text_similarity'),
    path('keywords/', KeywordExtractionView.as_view(), name='extract_keywords'),
    path('sentiment/', SentimentAnalysisView.as_view(), name='analyze_sentiment'),
]

# Speech Processing Endpoints
speech_patterns = [
    # Text-to-Speech
    path('tts/convert/', TextToSpeechView.as_view(), name='tts_convert'),
    path('tts/voices/', TextToSpeechView.as_view(), name='tts_voices'),
    
    # Speech-to-Text
    path('stt/transcribe/', SpeechToTextView.as_view(), name='stt_transcribe'),
    path('stt/languages/', SpeechToTextView.as_view(), name='stt_languages'),
    
    # Speech Settings
    path('tts/settings/', TextToSpeechView.as_view(), name='tts_settings'),
]

# Computer Vision Endpoints
cv_patterns = [
    # Face and Emotion Detection
    path('face-detection/', FaceDetectionView.as_view(), name='face_detection'),
    path('emotion-detection/', FaceDetectionView.as_view(), name='emotion_detection'),
    
    # Gesture Recognition
    path('gesture-recognition/', GestureRecognitionView.as_view(), name='gesture_recognition'),
    
    # Engagement Analysis
    path('engagement/', EngagementAnalysisView.as_view(), name='engagement_analysis'),
]

# Content Moderation Endpoints
moderation_patterns = [
    path('text/', ContentModerationView.as_view(), name='moderate_text'),
    path('image/', ContentModerationView.as_view(), name='moderate_image'),
    path('video/', ContentModerationView.as_view(), name='moderate_video'),
]

# Adaptive Learning Endpoints
adaptive_learning_patterns = [
    # Learning Path
    path('path/', LearningPathView.as_view(), name='learning_path'),
    
    # Analytics
    path('analytics/', LearningAnalyticsView.as_view(), name='learning_analytics'),
    
    # Recommendations
    path('recommendations/', LessonRecommendationView.as_view(), name='lesson_recommendations'),
    
    # User Profile
    path('profile/update/', UpdateLearningProfileView.as_view(), name='update_learning_profile'),
    
    # Lesson Tracking
    path('track/complete/<int:lesson_id>/', track_lesson_completion, name='track_lesson_completion'),
    path('track/lesson/', track_lesson_completion, name='track_lesson_completion_alt'),
    
    # Assessments
    path('assessments/', AssessmentView.as_view(), name='assessments_list'),
    path('assessments/<int:assessment_id>/', AssessmentView.as_view(), name='assessment_detail'),
    path('assessments/submit/', AssessmentView.as_view(), name='submit_assessment'),
]

# Analytics Endpoints
analytics_patterns = [
    path('engagement/', EngagementAnalyticsView.as_view(), name='engagement_analytics'),
    path('performance/', PerformanceAnalyticsView.as_view(), name='performance_analytics'),
    path('completion/', CompletionAnalyticsView.as_view(), name='completion_analytics'),
]

# ===== Root URL Patterns =====
urlpatterns = [
    # API Documentation
    path('', include(router.urls)),
    
    # API Documentation (Swagger/OpenAPI)
    path('docs/', include_docs_urls(
        title='SmartLearn AI API',
        description='AI services for SmartLearn Neuro',
        public=True
    ), name='api-docs'),
    
    # API Schema (OpenAPI)
    path('schema/', get_schema_view(
        title="SmartLearn AI API",
        description="AI services for SmartLearn Neuro",
        version="1.0.0"
    ), name='openapi-schema'),
    
    # Authentication
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Health Check
    path('health/', HealthCheckView.as_view(), name='health_check'),
    
    # API Endpoints
    path('text/', include((text_analysis_patterns, 'text'), namespace='text')),
    path('speech/', include((speech_patterns, 'speech'), namespace='speech')),
    path('vision/', include((cv_patterns, 'vision'), namespace='vision')),
    path('moderation/', include((moderation_patterns, 'moderation'), namespace='moderation')),
    path('learning/', include((adaptive_learning_patterns, 'learning'), namespace='learning')),
    path('analytics/', include((analytics_patterns, 'analytics'), namespace='analytics')),
    
    # API Root
    path('', views.api_root, name='api_root'),
]

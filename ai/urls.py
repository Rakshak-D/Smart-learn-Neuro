from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.documentation import include_docs_urls
from rest_framework.schemas import get_schema_view
# Temporarily comment out JWT imports to resolve import errors
# from rest_framework_simplejwt.views import TokenRefreshView

from . import views
from .views import (
    # Existing views
    TextToSpeechView,
    SpeechToTextView,
    FaceDetectionView,
    GestureRecognitionView,
    ContentModerationView,
    
    # Adaptive learning views
    LearningPathView,
    LearningAnalyticsView,
    LessonRecommendationView,
    UpdateLearningProfileView,
    track_lesson_completion,
    AssessmentView,
)

# API Router
router = DefaultRouter()

# Text-to-Speech Endpoints
tts_patterns = [
    path('convert/', TextToSpeechView.as_view(), name='tts_convert'),
    path('voices/', TextToSpeechView.as_view(), name='tts_voices'),
    path('settings/', TextToSpeechView.as_view(), name='tts_settings'),
]

# Speech-to-Text Endpoints
stt_patterns = [
    path('transcribe/', SpeechToTextView.as_view(), name='stt_transcribe'),
    path('languages/', SpeechToTextView.as_view(), name='stt_languages'),
]

# Computer Vision Endpoints
cv_patterns = [
    path('face-detection/', FaceDetectionView.as_view(), name='face_detection'),
    path('gesture-recognition/', GestureRecognitionView.as_view(), name='gesture_recognition'),
    path('emotion-detection/', FaceDetectionView.as_view(), name='emotion_detection'),
]

# Content Moderation
moderation_patterns = [
    path('text/', ContentModerationView.as_view(), name='moderate_text'),
    path('image/', ContentModerationView.as_view(), name='moderate_image'),
    path('video/', ContentModerationView.as_view(), name='moderate_video'),
]

# Adaptive Learning Endpoints
adaptive_learning_patterns = [
    # Learning path and progress
    path('learning-path/', LearningPathView.as_view(), name='learning_path'),
    path('analytics/', LearningAnalyticsView.as_view(), name='learning_analytics'),
    path('recommendations/', LessonRecommendationView.as_view(), name='lesson_recommendations'),
    path('update-profile/', UpdateLearningProfileView.as_view(), name='update_learning_profile'),
    path('track-lesson/', track_lesson_completion, name='track_lesson_completion'),
    
    # Assessments
    path('assessments/', AssessmentView.as_view(), name='assessments_list'),
    path('assessments/<int:assessment_id>/', AssessmentView.as_view(), name='assessment_detail'),
    path('assessments/submit/', AssessmentView.as_view(), name='submit_assessment'),
]

# Recommendation System - Temporarily commented out to resolve import errors
# recommendation_patterns = [
#     path('assessments/', RecommendationView.as_view(), name='recommend_assessments'),
#     path('resources/', RecommendationView.as_view(), name='recommend_resources'),
# ]

# URL Patterns
urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
    
    # Authentication
    # Temporarily comment out JWT token refresh URL
    # path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Text-to-Speech
    path('tts/', include(tts_patterns)),
    
    # Speech-to-Text
    path('stt/', include(stt_patterns)),
    
    # Computer Vision
    path('vision/', include(cv_patterns)),
    
    # Content Moderation
    path('moderation/', include(moderation_patterns)),
    
    # Adaptive Learning System
    path('learning/', include(adaptive_learning_patterns)),
    
    # Recommendation System - Temporarily commented out
    # path('recommend/', include(recommendation_patterns)),
    
    # API Documentation
    path('docs/', include_docs_urls(title='SmartLearn Neuro API')),
    
    # API Schema
    path('schema/', get_schema_view(
        title="SmartLearn Neuro API",
        description="API for SmartLearn Neuro - Adaptive Learning Platform",
        version="1.0.0"
    ), name='openapi-schema'),
    # Analytics Endpoints
    path('analytics/', include([
        path('engagement/', views.EngagementAnalyticsView.as_view(), name='engagement_analytics'),
        path('performance/', views.PerformanceAnalyticsView.as_view(), name='performance_analytics'),
        path('completion/', views.CompletionAnalyticsView.as_view(), name='completion_analytics'),
    ])),
    
    # Add a catch-all for the API root
    path('', views.api_root, name='api_root'),
]

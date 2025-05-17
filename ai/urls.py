from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RecommendationView, 
    process_gesture_view,
    AdaptiveLearningViewSet,
    TextToSpeechView,
    SpeechToTextView,
    FaceDetectionView,
    GestureRecognitionView,
    LearningAnalyticsViewSet,
    ContentModerationView,
    PersonalizationEngineViewSet
)

# API Router
router = DefaultRouter()
router.register(r'adaptive-learning', AdaptiveLearningViewSet, basename='adaptive_learning')
router.register(r'learning-analytics', LearningAnalyticsViewSet, basename='learning_analytics')
router.register(r'personalization', PersonalizationEngineViewSet, basename='personalization')

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

# Recommendation System
recommendation_patterns = [
    path('lessons/', RecommendationView.as_view(), name='recommend_lessons'),
    path('assessments/', RecommendationView.as_view(), name='recommend_assessments'),
    path('resources/', RecommendationView.as_view(), name='recommend_resources'),
]

# URL Patterns
urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
    
    # Text-to-Speech
    path('tts/', include(tts_patterns)),
    
    # Speech-to-Text
    path('stt/', include(stt_patterns)),
    
    # Computer Vision
    path('vision/', include(cv_patterns)),
    
    # Content Moderation
    path('moderation/', include(moderation_patterns)),
    
    # Recommendation System
    path('recommend/', include(recommendation_patterns)),
    
    # Gesture Processing
    path('gesture/process/', process_gesture_view, name='gesture_process'),
    
    # Feedback Processing
    path('feedback/', include([
        path('submit/', views.FeedbackView.as_view(), name='submit_feedback'),
        path('analytics/', views.FeedbackAnalyticsView.as_view(), name='feedback_analytics'),
    ])),
    
    # Analytics Endpoints
    path('analytics/', include([
        path('engagement/', views.EngagementAnalyticsView.as_view(), name='engagement_analytics'),
        path('performance/', views.PerformanceAnalyticsView.as_view(), name='performance_analytics'),
        path('retention/', views.RetentionAnalyticsView.as_view(), name='retention_analytics'),
    ])),
]

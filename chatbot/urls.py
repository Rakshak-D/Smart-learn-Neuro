from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'sessions', views.ChatSessionViewSet, basename='chatsession')
router.register(r'messages', views.ChatMessageViewSet, basename='chatmessage')
router.register(r'preferences', views.LearningPreferenceViewSet, basename='learningpreference')
router.register(r'feedback', views.UserFeedbackViewSet, basename='userfeedback')
router.register(r'knowledge', views.ChatbotKnowledgeBaseViewSet, basename='knowledgebase')

urlpatterns = [
    # API endpoints
    path('api/', include(router.urls)),
    
    # Break reminder check
    path('api/check-break/', views.check_break_reminder, name='check_break_reminder'),
    
    # Voice input processing
    path('api/process-voice/', views.process_voice_input, name='process_voice_input'),
    
    # Chat interface
    path('chat/', views.chat_interface, name='chat_interface'),
    path('chat/<uuid:session_id>/', views.chat_interface, name='chat_session'),
]

""
WebSocket routing for the AI app.
"""
from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    # WebSocket connection for real-time learning analytics
    re_path(r'ws/ai/analytics/(?P<user_id>\d+)/$', consumers.AnalyticsConsumer.as_asgi()),
    
    # WebSocket connection for adaptive learning sessions
    re_path(r'ws/ai/learning-session/(?P<session_id>[^/]+)/$', consumers.LearningSessionConsumer.as_asgi()),
    
    # WebSocket connection for real-time assessment monitoring
    re_path(r'ws/ai/assessment/(?P<attempt_id>\d+)/$', consumers.AssessmentConsumer.as_asgi()),
]

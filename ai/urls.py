from django.urls import path
from .views import RecommendationView, process_gesture_view

urlpatterns = [
    path('recommend/', RecommendationView.as_view(), name='recommend'),
    path('gesture/process/', process_gesture_view, name='gesture_process'),
]

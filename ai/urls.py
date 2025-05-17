from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RecommendationView, process_gesture_view

router = DefaultRouter()
router.register(r'recommend', RecommendationView)

urlpatterns = [
    path('recommend/', RecommendationView.as_view(), name='recommend'),
    path('gesture/process/', process_gesture_view, name='gesture_process'),
    path('api/', include(router.urls)),
]
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# API Router
router = DefaultRouter()
router.register(r'assessments', views.AssessmentViewSet, basename='assessment')
router.register(r'user-responses', views.UserResponseViewSet, basename='user-response')

# Assessment Patterns
app_name = 'assessments'

urlpatterns = [
    # API Endpoints
    path('api/', include(router.urls)),
    
    # Assessment URLs
    path('', views.assessment_list, name='assessment_list'),
    path('<int:pk>/', views.assessment_detail, name='assessment_detail'),
    path('<int:pk>/results/', views.assessment_results, name='assessment_results'),
]

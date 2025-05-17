from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Router for REST API endpoints
router = DefaultRouter()
router.register(r'assessments', views.AssessmentViewSet)
router.register(r'responses', views.ResponseViewSet)

urlpatterns = [
    # URL for list of assessments
    path('', views.assessment_list, name='assessment_list'),

    # URL for assessment detail - corrected path converter syntax
    path('<int:pk>/', views.assessment_detail, name='assessment_detail'),

    # URL for assessment results
    path('<int:pk>/results/', views.assessment_results, name='assessment_results'),

    # Include API routes
    path('api/', include(router.urls)),
]

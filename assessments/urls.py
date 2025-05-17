from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# API Router
router = DefaultRouter()
router.register(r'assessments', views.AssessmentViewSet, basename='assessment')
router.register(r'questions', views.QuestionViewSet, basename='question')
router.register(r'responses', views.ResponseViewSet, basename='response')
router.register(r'results', views.ResultViewSet, basename='result')
router.register(r'categories', views.CategoryViewSet, basename='category')

# Assessment Patterns
assessment_patterns = [
    path('', views.AssessmentListView.as_view(), name='assessment_list'),
    path('create/', views.AssessmentCreateView.as_view(), name='assessment_create'),
    path('<int:pk>/', views.AssessmentDetailView.as_view(), name='assessment_detail'),
    path('<int:pk>/update/', views.AssessmentUpdateView.as_view(), name='assessment_update'),
    path('<int:pk>/delete/', views.AssessmentDeleteView.as_view(), name='assessment_delete'),
    path('<int:pk>/start/', views.AssessmentStartView.as_view(), name='assessment_start'),
    path('<int:pk>/submit/', views.AssessmentSubmitView.as_view(), name='assessment_submit'),
    path('<int:pk>/questions/', views.QuestionListView.as_view(), name='question_list'),
    path('<int:pk>/results/', views.ResultListView.as_view(), name='result_list'),
]

# Question Patterns
question_patterns = [
    path('', views.QuestionListView.as_view(), name='question_list'),
    path('create/', views.QuestionCreateView.as_view(), name='question_create'),
    path('<int:qid>/', views.QuestionDetailView.as_view(), name='question_detail'),
    path('<int:qid>/update/', views.QuestionUpdateView.as_view(), name='question_update'),
    path('<int:qid>/delete/', views.QuestionDeleteView.as_view(), name='question_delete'),
]

# Result Patterns
result_patterns = [
    path('', views.ResultListView.as_view(), name='result_list'),
    path('<int:rid>/', views.ResultDetailView.as_view(), name='result_detail'),
    path('<int:rid>/pdf/', views.ResultPDFView.as_view(), name='result_pdf'),
    path('<int:rid>/share/', views.ResultShareView.as_view(), name='result_share'),
    path('progress/', views.ProgressView.as_view(), name='progress'),
]

# Audio Assessment Patterns
audio_assessment_patterns = [
    path('start/', views.AudioAssessmentStartView.as_view(), name='audio_assessment_start'),
    path('record/', views.AudioRecordingView.as_view(), name='audio_record'),
    path('submit/', views.AudioSubmissionView.as_view(), name='audio_submit'),
    path('results/<int:pk>/', views.AudioResultView.as_view(), name='audio_result'),
]

# Adaptive Assessment Patterns
adaptive_assessment_patterns = [
    path('start/', views.AdaptiveAssessmentStartView.as_view(), name='adaptive_assessment_start'),
    path('next-question/', views.AdaptiveQuestionView.as_view(), name='adaptive_next_question'),
    path('submit-answer/', views.AdaptiveAnswerView.as_view(), name='adaptive_submit_answer'),
    path('results/<int:pk>/', views.AdaptiveResultView.as_view(), name='adaptive_result'),
]

# Practice Test Patterns
practice_patterns = [
    path('', views.PracticeTestListView.as_view(), name='practice_list'),
    path('start/<int:pk>/', views.PracticeTestStartView.as_view(), name='practice_start'),
    path('question/<int:qid>/', views.PracticeQuestionView.as_view(), name='practice_question'),
    path('submit/<int:pk>/', views.PracticeSubmitView.as_view(), name='practice_submit'),
    path('results/<int:pk>/', views.PracticeResultView.as_view(), name='practice_result'),
]

# URL Patterns
urlpatterns = [
    # API Endpoints
    path('api/', include(router.urls)),
    
    # Assessments
    path('', include(assessment_patterns)),
    
    # Questions
    path('questions/', include(question_patterns)),
    
    # Results
    path('results/', include(result_patterns)),
    
    # Audio Assessments
    path('audio/', include(audio_assessment_patterns)),
    
    # Adaptive Assessments
    path('adaptive/', include(adaptive_assessment_patterns)),
    
    # Practice Tests
    path('practice/', include(practice_patterns)),
    
    # Categories
    path('categories/', include([
        path('', views.CategoryListView.as_view(), name='category_list'),
        path('<int:pk>/', views.CategoryDetailView.as_view(), name='category_detail'),
        path('<int:pk>/assessments/', views.CategoryAssessmentsView.as_view(), name='category_assessments'),
    ])),
    
    # Reports
    path('reports/', include([
        path('progress/', views.ProgressReportView.as_view(), name='progress_report'),
        path('performance/', views.PerformanceReportView.as_view(), name='performance_report'),
        path('analytics/', views.AnalyticsDashboardView.as_view(), name='analytics_dashboard'),
    ])),
    
    # WebSocket Endpoints
    path('ws/', include([
        path('assessments/<int:pk>/', views.AssessmentConsumer.as_asgi()),
        path('audio/record/', views.AudioRecordingConsumer.as_asgi()),
    ])),
]

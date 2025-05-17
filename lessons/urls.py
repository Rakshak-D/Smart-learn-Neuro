from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from . import views

# API Router
router = DefaultRouter()
router.register(r'lessons', views.LessonViewSet, basename='lesson')
router.register(r'modules', views.ModuleViewSet, basename='module')
router.register(r'courses', views.CourseViewSet, basename='course')
router.register(r'progress', views.LessonProgressViewSet, basename='lesson-progress')
router.register(r'bookmarks', views.BookmarkViewSet, basename='bookmark')
router.register(r'notes', views.NoteViewSet, basename='note')

# Lesson Patterns
lesson_patterns = [
    path('', views.LessonListView.as_view(), name='lesson_list'),
    path('create/', views.LessonCreateView.as_view(), name='lesson_create'),
    path('<int:pk>/', views.LessonDetailView.as_view(), name='lesson_detail'),
    path('<int:pk>/update/', views.LessonUpdateView.as_view(), name='lesson_update'),
    path('<int:pk>/delete/', views.LessonDeleteView.as_view(), name='lesson_delete'),
    path('<int:pk>/start/', views.LessonStartView.as_view(), name='lesson_start'),
    path('<int:pk>/complete/', views.LessonCompleteView.as_view(), name='lesson_complete'),
    path('<int:pk>/bookmark/', views.BookmarkToggleView.as_view(), name='lesson_bookmark'),
    path('<int:pk>/note/', views.NoteCreateView.as_view(), name='lesson_note_create'),
    path('<int:pk>/download/', views.LessonDownloadView.as_view(), name='lesson_download'),
    path('<int:pk>/print/', views.LessonPrintView.as_view(), name='lesson_print'),
    path('<int:pk>/rate/', views.LessonRateView.as_view(), name='lesson_rate'),
    path('<int:pk>/share/', views.LessonShareView.as_view(), name='lesson_share'),
]

# Module Patterns
module_patterns = [
    path('', views.ModuleListView.as_view(), name='module_list'),
    path('create/', views.ModuleCreateView.as_view(), name='module_create'),
    path('<int:pk>/', views.ModuleDetailView.as_view(), name='module_detail'),
    path('<int:pk>/update/', views.ModuleUpdateView.as_view(), name='module_update'),
    path('<int:pk>/delete/', views.ModuleDeleteView.as_view(), name='module_delete'),
    path('<int:pk>/lessons/', views.ModuleLessonsView.as_view(), name='module_lessons'),
    path('<int:pk>/progress/', views.ModuleProgressView.as_view(), name='module_progress'),
]

# Course Patterns
course_patterns = [
    path('', views.CourseListView.as_view(), name='course_list'),
    path('create/', views.CourseCreateView.as_view(), name='course_create'),
    path('<int:pk>/', views.CourseDetailView.as_view(), name='course_detail'),
    path('<int:pk>/update/', views.CourseUpdateView.as_view(), name='course_update'),
    path('<int:pk>/delete/', views.CourseDeleteView.as_view(), name='course_delete'),
    path('<int:pk>/enroll/', views.CourseEnrollView.as_view(), name='course_enroll'),
    path('<int:pk>/unenroll/', views.CourseUnenrollView.as_view(), name='course_unenroll'),
    path('<int:pk>/progress/', views.CourseProgressView.as_view(), name='course_progress'),
    path('<int:pk>/certificate/', views.CourseCertificateView.as_view(), name='course_certificate'),
    path('<int:pk>/rate/', views.CourseRateView.as_view(), name='course_rate'),
    path('<int:pk>/review/', views.CourseReviewView.as_view(), name='course_review'),
]

# Learning Path Patterns
learning_path_patterns = [
    path('', views.LearningPathListView.as_view(), name='learning_path_list'),
    path('create/', views.LearningPathCreateView.as_view(), name='learning_path_create'),
    path('<int:pk>/', views.LearningPathDetailView.as_view(), name='learning_path_detail'),
    path('<int:pk>/update/', views.LearningPathUpdateView.as_view(), name='learning_path_update'),
    path('<int:pk>/delete/', views.LearningPathDeleteView.as_view(), name='learning_path_delete'),
    path('<int:pk>/enroll/', views.LearningPathEnrollView.as_view(), name='learning_path_enroll'),
    path('<int:pk>/progress/', views.LearningPathProgressView.as_view(), name='learning_path_progress'),
    path('<int:pk>/recommend/', views.LearningPathRecommendView.as_view(), name='learning_path_recommend'),
]

# Search and Discovery
search_patterns = [
    path('', views.SearchView.as_view(), name='search'),
    path('suggestions/', views.SearchSuggestionsView.as_view(), name='search_suggestions'),
    path('filters/', views.SearchFiltersView.as_view(), name='search_filters'),
    path('recent/', views.RecentSearchesView.as_view(), name='recent_searches'),
    path('popular/', views.PopularSearchesView.as_view(), name='popular_searches'),
]

# Analytics and Reports
analytics_patterns = [
    path('progress/', views.ProgressAnalyticsView.as_view(), name='progress_analytics'),
    path('performance/', views.PerformanceAnalyticsView.as_view(), name='performance_analytics'),
    path('engagement/', views.EngagementAnalyticsView.as_view(), name='engagement_analytics'),
    path('completion/', views.CompletionAnalyticsView.as_view(), name='completion_analytics'),
    path('export/', views.ExportAnalyticsView.as_view(), name='export_analytics'),
]

# URL Patterns
urlpatterns = [
    # API Endpoints
    path('api/', include(router.urls)),
    
    # Lessons
    path('lessons/', include(lesson_patterns)),
    
    # Modules
    path('modules/', include(module_patterns)),
    
    # Courses
    path('courses/', include(course_patterns)),
    
    # Learning Paths
    path('learning-paths/', include(learning_path_patterns)),
    
    # Search and Discovery
    path('search/', include(search_patterns)),
    
    # Analytics and Reports
    path('analytics/', include(analytics_patterns)),
    
    # User-specific content
    path('my/', include([
        path('lessons/', views.MyLessonsView.as_view(), name='my_lessons'),
        path('courses/', views.MyCoursesView.as_view(), name='my_courses'),
        path('bookmarks/', views.MyBookmarksView.as_view(), name='my_bookmarks'),
        path('notes/', views.MyNotesView.as_view(), name='my_notes'),
        path('progress/', views.MyProgressView.as_view(), name='my_progress'),
        path('certificates/', views.MyCertificatesView.as_view(), name='my_certificates'),
    ])),
    
    # WebSocket Endpoints
    path('ws/', include([
        path('lessons/<int:pk>/', views.LessonConsumer.as_asgi()),
        path('progress/<int:user_id>/', views.ProgressConsumer.as_asgi()),
    ])),
]

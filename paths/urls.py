from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from . import views

# API Router
router = DefaultRouter()
router.register(r'paths', views.LearningPathViewSet, basename='learningpath')
router.register(r'user-paths', views.UserPathViewSet, basename='userpath')
router.register(r'path-items', views.PathItemViewSet, basename='pathitem')
router.register(r'recommendations', views.RecommendationViewSet, basename='recommendation')

# Learning Path Patterns
path_patterns = [
    path('', views.LearningPathListView.as_view(), name='path_list'),
    path('create/', views.LearningPathCreateView.as_view(), name='path_create'),
    path('<int:pk>/', views.LearningPathDetailView.as_view(), name='path_detail'),
    path('<int:pk>/update/', views.LearningPathUpdateView.as_view(), name='path_update'),
    path('<int:pk>/delete/', views.LearningPathDeleteView.as_view(), name='path_delete'),
    path('<int:pk>/publish/', views.LearningPathPublishView.as_view(), name='path_publish'),
    path('<int:pk>/unpublish/', views.LearningPathUnpublishView.as_view(), name='path_unpublish'),
    path('<int:pk>/clone/', views.LearningPathCloneView.as_view(), name='path_clone'),
    path('<int:pk>/export/', views.LearningPathExportView.as_view(), name='path_export'),
    path('<int:pk>/share/', views.LearningPathShareView.as_view(), name='path_share'),
    path('<int:pk>/collaborators/', views.LearningPathCollaboratorsView.as_view(), name='path_collaborators'),
    path('<int:pk>/stats/', views.LearningPathStatsView.as_view(), name='path_stats'),
]

# User Path Patterns
user_path_patterns = [
    path('', views.UserPathListView.as_view(), name='user_path_list'),
    path('create/', views.UserPathCreateView.as_view(), name='user_path_create'),
    path('<int:pk>/', views.UserPathDetailView.as_view(), name='user_path_detail'),
    path('<int:pk>/update/', views.UserPathUpdateView.as_view(), name='user_path_update'),
    path('<int:pk>/delete/', views.UserPathDeleteView.as_view(), name='user_path_delete'),
    path('<int:pk>/start/', views.UserPathStartView.as_view(), name='user_path_start'),
    path('<int:pk>/complete/', views.UserPathCompleteView.as_view(), name='user_path_complete'),
    path('<int:pk>/progress/', views.UserPathProgressView.as_view(), name='user_path_progress'),
    path('<int:pk>/certificate/', views.UserPathCertificateView.as_view(), name='user_path_certificate'),
]

# Path Item Patterns
path_item_patterns = [
    path('', views.PathItemListView.as_view(), name='path_item_list'),
    path('create/', views.PathItemCreateView.as_view(), name='path_item_create'),
    path('<int:pk>/', views.PathItemDetailView.as_view(), name='path_item_detail'),
    path('<int:pk>/update/', views.PathItemUpdateView.as_view(), name='path_item_update'),
    path('<int:pk>/delete/', views.PathItemDeleteView.as_view(), name='path_item_delete'),
    path('<int:pk>/move-up/', views.PathItemMoveUpView.as_view(), name='path_item_move_up'),
    path('<int:pk>/move-down/', views.PathItemMoveDownView.as_view(), name='path_item_move_down'),
    path('reorder/', views.PathItemReorderView.as_view(), name='path_item_reorder'),
]

# Recommendation Patterns
recommendation_patterns = [
    path('', views.RecommendationListView.as_view(), name='recommendation_list'),
    path('paths/', views.PathRecommendationView.as_view(), name='path_recommendations'),
    path('courses/', views.CourseRecommendationView.as_view(), name='course_recommendations'),
    path('lessons/', views.LessonRecommendationView.as_view(), name='lesson_recommendations'),
    path('assessments/', views.AssessmentRecommendationView.as_view(), name='assessment_recommendations'),
    path('personalized/', views.PersonalizedRecommendationView.as_view(), name='personalized_recommendations'),
]

# Analytics Patterns
analytics_patterns = [
    path('engagement/', views.EngagementAnalyticsView.as_view(), name='engagement_analytics'),
    path('completion/', views.CompletionAnalyticsView.as_view(), name='completion_analytics'),
    path('performance/', views.PerformanceAnalyticsView.as_view(), name='performance_analytics'),
    path('retention/', views.RetentionAnalyticsView.as_view(), name='retention_analytics'),
    path('export/', views.ExportAnalyticsView.as_view(), name='export_analytics'),
]

# URL Patterns
urlpatterns = [
    # API Endpoints
    path('api/', include(router.urls)),
    
    # Learning Paths
    path('', include(path_patterns)),
    
    # User Paths
    path('my-paths/', include(user_path_patterns)),
    
    # Path Items
    path('items/', include(path_item_patterns)),
    
    # Recommendations
    path('recommend/', include(recommendation_patterns)),
    
    # Analytics
    path('analytics/', include(analytics_patterns)),
    
    # Discovery
    path('discover/', include([
        path('', views.DiscoverPathsView.as_view(), name='discover_paths'),
        path('featured/', views.FeaturedPathsView.as_view(), name='featured_paths'),
        path('popular/', views.PopularPathsView.as_view(), name='popular_paths'),
        path('trending/', views.TrendingPathsView.as_view(), name='trending_paths'),
        path('categories/', views.PathCategoriesView.as_view(), name='path_categories'),
        path('category/<slug:category_slug>/', views.PathCategoryDetailView.as_view(), name='path_category_detail'),
    ])),
    
    # WebSocket Endpoints
    path('ws/', include([
        path('paths/<int:path_id>/', views.PathConsumer.as_asgi()),
        path('user-paths/<int:user_id>/', views.UserPathConsumer.as_asgi()),
    ])),
]

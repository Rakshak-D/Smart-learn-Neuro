from django.urls import path, include, re_path
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from . import views

# API Router
router = DefaultRouter()
router.register(r'users', views.CustomUserViewSet, basename='user')
router.register(r'profiles', views.UserProfileViewSet, basename='profile')

# JWT Authentication
jwt_patterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]

# User Management
user_patterns = [
    # Authentication
    path('login/', views.LoginView.as_view(), name='login'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    
    # Password Management
    path('password/change/', views.PasswordChangeView.as_view(), name='password_change'),
    path('password/reset/', views.PasswordResetView.as_view(), name='password_reset'),
    path('password/reset/confirm/<uidb64>/<token>/', 
         views.PasswordResetConfirmView.as_view(), 
         name='password_reset_confirm'),
    
    # Email Verification
    path('verify-email/', views.VerifyEmailView.as_view(), name='verify_email'),
    path('verify-email/confirm/<str:key>/', 
         views.VerifyEmailConfirmView.as_view(), 
         name='verify_email_confirm'),
    
    # Profile Management
    path('me/', views.CurrentUserView.as_view(), name='current_user'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('settings/', views.SettingsView.as_view(), name='settings'),
    path('preferences/', views.PreferencesView.as_view(), name='preferences'),
    
    # Notifications
    path('notifications/', include([
        path('', views.NotificationListView.as_view(), name='notifications'),
        path('unread/', views.UnreadNotificationsView.as_view(), name='unread_notifications'),
        path('mark-all-read/', views.MarkAllAsReadView.as_view(), name='mark_all_read'),
        path('<int:pk>/', views.NotificationDetailView.as_view(), name='notification_detail'),
    ])),
]

# API Endpoints
api_patterns = [
    path('', include(router.urls)),
    path('auth/', include(jwt_patterns)),
    path('users/', include(user_patterns)),
]

# URL Patterns
urlpatterns = [
    # API Endpoints
    path('api/', include(api_patterns)),
    
    # Frontend Routes (handled by Vue/React)
    # These routes are for frontend routing and will be handled by the SPA
    re_path(r'^.*$', TemplateView.as_view(template_name='index.html')),
]
# SmartLearnNeuro/urls.py

from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt

# API Versioning
urlpatterns = [
    # Admin site URL
    path('admin/', admin.site.urls),
    
    # API Version 1
    path('api/v1/', include([
        # User authentication and profile management
        path('auth/', include('users.urls')),
        
        # Lessons module
        path('lessons/', include('lessons.urls')),
        
        # Assessments module
        path('assessments/', include('assessments.urls')),
        
        # Learning paths
        path('paths/', include('paths.urls')),
        
        # AI features
        path('ai/', include('ai.urls')),
        
        # Accessibility features
        path('accessibility/', include('accessibility.urls')),
    ])),
    
    # WebSocket URL for real-time features
    re_path(r'^ws/', include([
        path('notifications/', include('notifications.urls')),
        path('assessments/', include('assessments.ws_urls')),
    ])),
    
    # Service Worker for PWA
    path('sw.js', TemplateView.as_view(
        template_name='sw.js',
        content_type='application/javascript',
    ), name='service_worker'),
    
    # Offline page
    path('offline/', TemplateView.as_view(template_name='offline.html'), name='offline'),
]

# Error handlers
handler400 = 'core.views.bad_request'
handler403 = 'core.views.permission_denied'
handler404 = 'core.views.page_not_found'
handler500 = 'core.views.server_error'

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Debug toolbar
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns

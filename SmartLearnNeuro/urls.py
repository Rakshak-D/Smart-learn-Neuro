# SmartLearnNeuro/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Define all the URL routes for the project
urlpatterns = [
    # Admin site URL
    path('admin/', admin.site.urls),

    # User authentication and profile management (login, register, settings)
    path('', include('users.urls')),

    # Lessons module (list, detail, progress)
    path('lessons/', include('lessons.urls')),

    # Assessments module (quizzes, audio assessments)
    path('assessments/', include('assessments.urls')),

    # Personalized learning paths
    path('paths/', include('paths.urls')),

    # Accessibility features (dyslexia font toggle, etc.)
    path('accessibility/', include('accessibility.urls')),

    # AI-based recommendations or tools
    path('ai/', include('ai.urls')),
]

# Serve media files (uploaded images, audio, etc.) during development
# In production, you should use a proper media server (like Amazon S3 or Nginx)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

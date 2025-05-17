from django.urls import path
from . import views

urlpatterns = [
    # URL route for accessibility settings page
    path('settings/', views.accessibility_settings, name='accessibility_settings'),
]

from django.conf import settings
from django.utils.functional import SimpleLazyObject
from .models import AccessibilitySettings, DyslexiaSettings, ADHDSettings


def get_accessibility_settings(request):
    if not hasattr(request, '_cached_accessibility_settings'):
        if request.user.is_authenticated:
            request._cached_accessibility_settings = {
                'general': request.user.accessibility_settings,
                'dyslexia': request.user.dyslexia_settings,
                'adhd': request.user.adhd_settings,
            }
        else:
            # Default settings for anonymous users
            request._cached_accessibility_settings = {
                'general': AccessibilitySettings(),
                'dyslexia': DyslexiaSettings(),
                'adhd': ADHDSettings(),
            }
    return request._cached_accessibility_settings


class AccessibilityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Add accessibility settings to the request
        request.accessibility = SimpleLazyObject(lambda: get_accessibility_settings(request))
        
        # Process the request
        response = self.get_response(request)
        
        # Add accessibility context to template responses
        if hasattr(response, 'render') and callable(response.render):
            if not hasattr(response, 'context_data') or response.context_data is None:
                response.context_data = {}
                
            # Add accessibility settings to template context
            response.context_data['accessibility'] = request.accessibility
            
            # For backward compatibility, add commonly used settings to the root context
            if request.user.is_authenticated:
                response.context_data.update({
                    'font_size': request.accessibility['dyslexia'].font_size,
                    'font_family': request.accessibility['dyslexia'].font_family,
                    'high_contrast': request.accessibility['general'].is_high_contrast,
                    'dark_mode': request.accessibility['general'].is_dark_mode,
                })
            else:
                # Default values for unauthenticated users
                response.context_data.update({
                    'font_size': 16,
                    'font_family': 'Arial',
                    'high_contrast': False,
                    'dark_mode': False,
                })
        
        return response
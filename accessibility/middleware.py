from django.conf import settings
from .models import AccessibilitySettings

class AccessibilityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_template_response(self, request, response):
        if hasattr(response, 'context_data') and response.context_data is not None:
            if request.user.is_authenticated:
                settings, _ = AccessibilitySettings.objects.get_or_create(user=request.user)
                response.context_data['font_size'] = request.user.font_size  # Ensure font_size is from CustomUser
            else:
                response.context_data['font_size'] = 16  # Default font size for unauthenticated users
        return response
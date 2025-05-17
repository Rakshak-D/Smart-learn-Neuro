from accessibility.models import AccessibilitySettings

def user_settings(request):
    if request.user.is_authenticated:
        settings, created = AccessibilitySettings.objects.get_or_create(user=request.user)
        return {'accessibility_settings': settings}
    return {'accessibility_settings': None}

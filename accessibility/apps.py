from django.apps import AppConfig

class AccessibilityConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accessibility'
    
    def ready(self):
        # Import and register signals
        from . import signals  # noqa

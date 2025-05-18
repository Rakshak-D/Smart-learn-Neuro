from django.apps import AppConfig


class AiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ai'
    verbose_name = 'AI Services'
    
    def ready(self):
        # Import signals to register them
        import ai.signals  # noqa

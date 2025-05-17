from django.db import models
from django.conf import settings

class AccessibilitySettings(models.Model):
    # One-to-one relation to the User model
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # Whether to use a dyslexia-friendly font
    use_dyslexia_font = models.BooleanField(default=False)

    def __str__(self):
        return f"Settings for {self.user.username}"

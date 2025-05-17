from django.contrib.auth.models import AbstractUser
from django.db import models

# This is a custom user model that extends Django's default AbstractUser
# It adds fields specifically useful for accessibility and personalization
class CustomUser(AbstractUser):
    # Field to let users choose their preferred font size for better readability
    font_size = models.PositiveIntegerField(default=16)

    # Toggle for users who prefer audio-based content (e.g., TTS or audio lessons)
    prefers_audio = models.BooleanField(default=False)

    # Toggle for users who prefer their lessons to be shown in small chunks
    prefers_chunked = models.BooleanField(default=True)

    # String representation of the user model (used in admin interface and logs)
    def __str__(self):
        return self.username

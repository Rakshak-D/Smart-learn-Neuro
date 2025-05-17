from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

# User learning styles and conditions
LEARNING_CONDITIONS = [
    ('ADHD', 'Attention Deficit Hyperactivity Disorder'),
    ('DYSLEXIA', 'Dyslexia'),
    ('NORMAL', 'Normal Learner'),
]

# Font families for dyslexia support
FONT_FAMILIES = [
    ('Arial', 'Arial'),
    ('OpenDyslexic', 'OpenDyslexic'),
    ('ComicSans', 'Comic Sans'),
    ('Helvetica', 'Helvetica'),
]

class CustomUser(AbstractUser):
    # Basic user information
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    class_level = models.CharField(max_length=20)
    learning_condition = models.CharField(max_length=20, choices=LEARNING_CONDITIONS)
    
    # Accessibility and personalization settings
    font_size = models.PositiveIntegerField(default=16)
    font_family = models.CharField(max_length=50, choices=FONT_FAMILIES, default='Arial')
    prefers_audio = models.BooleanField(default=False)
    prefers_chunked = models.BooleanField(default=True)
    background_color = models.CharField(max_length=20, default='#ffffff')
    text_color = models.CharField(max_length=20, default='#000000')
    contrast_mode = models.BooleanField(default=False)
    
    # ADHD specific settings
    focus_timer = models.PositiveIntegerField(default=25)  # in minutes
    break_duration = models.PositiveIntegerField(default=5)  # in minutes
    engagement_level = models.FloatField(default=1.0)  # 0-1 scale
    
    # Dyslexia specific settings
    letter_spacing = models.FloatField(default=1.0)
    word_spacing = models.FloatField(default=1.0)
    line_height = models.FloatField(default=1.5)
    
    # Learning analytics
    last_active = models.DateTimeField(default=timezone.now)
    progress = models.JSONField(default=dict)
    performance_history = models.JSONField(default=list)
    preferred_learning_style = models.CharField(max_length=50, blank=True)
    
    def __str__(self):
        return f"{self.name} ({self.learning_condition})"

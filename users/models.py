from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

# User learning styles and conditions
LEARNING_CONDITIONS = [
    ('ADHD', 'Attention Deficit Hyperactivity Disorder'),
    ('DYSLEXIA', 'Dyslexia'),
    ('NORMAL', 'Normal Learner'),
]

class LearningStyle(models.Model):
    """Model to store different learning styles and preferences"""
    name = models.CharField(max_length=50)
    description = models.TextField()
    icon = models.CharField(max_length=50, blank=True)
    
    def __str__(self):
        return self.name

class CustomUser(AbstractUser):
    # Basic user information
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    class_level = models.CharField(max_length=20)
    learning_condition = models.CharField(max_length=20, choices=LEARNING_CONDITIONS)
    date_of_birth = models.DateField(null=True, blank=True)
    
    # Learning preferences
    prefers_audio = models.BooleanField(default=False)
    prefers_video = models.BooleanField(default=True)
    prefers_text = models.BooleanField(default=True)
    prefers_chunked = models.BooleanField(default=True)
    
    # Engagement tracking
    engagement_level = models.FloatField(
        default=1.0,  # 0-1 scale
        validators=[MinValueValidator(0), MaxValueValidator(1)]
    )
    
    # Methods to access accessibility settings
    @property
    def accessibility_settings(self):
        from accessibility.models import AccessibilitySettings
        return AccessibilitySettings.objects.get_or_create(user=self)[0]
    
    @property
    def dyslexia_settings(self):
        from accessibility.models import DyslexiaSettings
        return DyslexiaSettings.objects.get_or_create(user=self)[0]
    
    @property
    def adhd_settings(self):
        from accessibility.models import ADHDSettings
        return ADHDSettings.objects.get_or_create(user=self)[0]
    
    # Learning analytics
    last_active = models.DateTimeField(default=timezone.now)
    total_learning_time = models.PositiveIntegerField(default=0)  # in minutes
    learning_streak = models.PositiveIntegerField(default=0)  # consecutive days
    preferred_learning_styles = models.ManyToManyField(LearningStyle, blank=True)
    
    # Progress tracking
    current_lesson = models.ForeignKey(
        'lessons.Lesson',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='current_lesson_users'
    )
    completed_lessons = models.ManyToManyField(
        'lessons.Lesson',
        blank=True,
        related_name='completed_by_users'
    )
    
    # AI and personalization
    learning_pace = models.CharField(max_length=20, default='medium')  # slow, medium, fast
    difficulty_level = models.CharField(max_length=20, default='beginner')  # beginner, intermediate, advanced
    
    # Progress and performance
    progress = models.JSONField(default=dict)
    performance_history = models.JSONField(default=list)
    learning_goals = models.JSONField(default=list)
    
    # Parent/Teacher connection
    parent_email = models.EmailField(blank=True, null=True)
    teacher_email = models.EmailField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']
    
    def __str__(self):
        return f"{self.name} ({self.get_learning_condition_display()})"
    
    def update_learning_analytics(self, lesson_duration, score=None):
        """Update user's learning analytics after completing a lesson"""
        self.total_learning_time += lesson_duration
        
        # Update learning streak
        today = timezone.now().date()
        last_active_date = self.last_active.date()
        if last_active_date == today - timezone.timedelta(days=1):
            self.learning_streak += 1
        elif last_active_date < today - timezone.timedelta(days=1):
            self.learning_streak = 1
            
        # Update difficulty level based on performance
        if score is not None:
            if score > 80 and self.difficulty_level != 'advanced':
                self.difficulty_level = 'intermediate' if self.difficulty_level == 'beginner' else 'advanced'
            elif score < 50 and self.difficulty_level != 'beginner':
                self.difficulty_level = 'intermediate' if self.difficulty_level == 'advanced' else 'beginner'
        
        self.last_active = timezone.now()
        self.save()
    
    def get_accessibility_settings(self):
        """Return user's accessibility settings as a dictionary"""
        return {
            'font_size': self.font_size,
            'font_family': self.font_family,
            'color_theme': self.color_theme,
            'contrast_mode': self.contrast_mode,
            'letter_spacing': self.letter_spacing,
            'word_spacing': self.word_spacing,
            'line_height': self.line_height,
            'speech_rate': self.speech_rate,
            'voice_type': self.voice_type,
            'enable_syllable_division': self.enable_syllable_division,
            'enable_highlighting': self.enable_highlighting,
        }
    
    def get_learning_preferences(self):
        """Return user's learning preferences as a dictionary"""
        return {
            'prefers_audio': self.prefers_audio,
            'prefers_video': self.prefers_video,
            'prefers_text': self.prefers_text,
            'prefers_chunked': self.prefers_chunked,
            'learning_pace': self.learning_pace,
            'difficulty_level': self.difficulty_level,
            'learning_styles': [style.name for style in self.preferred_learning_styles.all()]
        }

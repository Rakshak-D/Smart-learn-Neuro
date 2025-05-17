from django.db import models
from django.conf import settings
from django.utils import timezone

# Choices for different settings
FONT_CHOICES = [
    ('default', 'Default'),
    ('open_dyslexic', 'OpenDyslexic'),
    ('comic_sans', 'Comic Sans MS'),
    ('arial', 'Arial'),
    ('verdana', 'Verdana'),
    ('tahoma', 'Tahoma'),
]

COLOR_THEME_CHOICES = [
    ('default', 'Default'),
    ('high_contrast', 'High Contrast'),
    ('dark', 'Dark Mode'),
    ('light', 'Light Mode'),
    ('sepia', 'Sepia'),
    ('blue_light_filter', 'Blue Light Filter'),
]

BREAK_INTERVAL_CHOICES = [
    (5, '5 minutes'),
    (10, '10 minutes'),
    (15, '15 minutes'),
    (20, '20 minutes'),
    (30, '30 minutes'),
]

READING_GUIDE_CHOICES = [
    ('none', 'None'),
    ('line', 'Line Guide'),
    ('ruler', 'Reading Ruler'),
    ('highlight', 'Highlight Current Line'),
    ('mask', 'Screen Mask'),
]

# Base class for all accessibility settings
class AccessibilitySettings(models.Model):
    # One-to-one relation to the User model
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # Date these settings were last modified
    last_modified = models.DateTimeField(auto_now=True)
    
    # General preferences that apply to all users
    is_screen_reader_active = models.BooleanField(default=False)
    enable_keyboard_navigation = models.BooleanField(default=False)
    enable_voice_control = models.BooleanField(default=False)
    enable_offline_access = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Accessibility Settings for {self.user.username}"


# Specific settings for dyslexia users
class DyslexiaSettings(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # Text and reading preferences
    font_family = models.CharField(max_length=20, choices=FONT_CHOICES, default='default')
    font_size = models.PositiveIntegerField(default=16)  # Size in pixels
    font_weight = models.CharField(max_length=10, default='normal')
    line_spacing = models.FloatField(default=1.5)  # Multiplier for line spacing
    letter_spacing = models.FloatField(default=0.12)  # em units
    word_spacing = models.FloatField(default=0.16)  # em units
    
    # Color and contrast
    color_theme = models.CharField(max_length=20, choices=COLOR_THEME_CHOICES, default='default')
    use_custom_colors = models.BooleanField(default=False)
    text_color = models.CharField(max_length=7, default='#000000')  # Hex format
    background_color = models.CharField(max_length=7, default='#FFFFFF')  # Hex format
    
    # Reading aids
    reading_guide = models.CharField(max_length=20, choices=READING_GUIDE_CHOICES, default='none')
    reading_guide_color = models.CharField(max_length=7, default='#FFFF00')  # Hex format
    
    # Text processing
    enable_text_to_speech = models.BooleanField(default=False)
    tts_voice = models.CharField(max_length=30, default='default')
    tts_speed = models.FloatField(default=1.0)  # Multiplier
    enable_speech_to_text = models.BooleanField(default=False)
    
    # Content formatting
    enable_content_chunking = models.BooleanField(default=True)
    enable_spelling_assistance = models.BooleanField(default=True)
    enable_grammar_assistance = models.BooleanField(default=True)
    simplified_language = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Dyslexia Settings for {self.user.username}"


# Specific settings for ADHD users
class ADHDSettings(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # Focus and attention
    enable_focus_mode = models.BooleanField(default=False)
    focus_level = models.IntegerField(default=1, choices=[(1, 'Minimal'), (2, 'Medium'), (3, 'Maximum')])
    enable_white_noise = models.BooleanField(default=False)
    white_noise_type = models.CharField(max_length=20, default='white')
    
    # Break reminders
    enable_break_reminders = models.BooleanField(default=True)
    break_interval = models.IntegerField(choices=BREAK_INTERVAL_CHOICES, default=15)
    break_duration = models.IntegerField(default=3)  # In minutes
    
    # Visual aids and organization
    show_visual_timers = models.BooleanField(default=True)
    show_progress_bars = models.BooleanField(default=True)
    enable_task_chunking = models.BooleanField(default=True)
    max_task_duration = models.IntegerField(default=10)  # In minutes
    
    # Rewards and gamification
    enable_rewards_system = models.BooleanField(default=True)
    reward_frequency = models.IntegerField(default=3)  # How often to give rewards
    reward_animations = models.BooleanField(default=True)
    
    # UI preferences
    reduce_animations = models.BooleanField(default=False)
    use_simplified_interface = models.BooleanField(default=True)
    
    def __str__(self):
        return f"ADHD Settings for {self.user.username}"


# Track break and activity sessions for ADHD users
class ActivitySession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    session_type = models.CharField(max_length=20, choices=[
        ('study', 'Study Session'),
        ('break', 'Break Session'),
    ])
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)
    duration = models.IntegerField(null=True, blank=True)  # In seconds
    activity = models.CharField(max_length=255, null=True, blank=True)  # What was done
    
    def save(self, *args, **kwargs):
        if self.end_time and not self.duration:
            diff = self.end_time - self.start_time
            self.duration = diff.total_seconds()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.session_type} for {self.user.username} on {self.start_time.strftime('%Y-%m-%d %H:%M')}"


# Reading guide positions for dyslexia users
class ReadingGuidePosition(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    page_url = models.CharField(max_length=255)  # URL or identifier of the content
    position_y = models.IntegerField()  # Vertical position in pixels
    timestamp = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'page_url')
    
    def __str__(self):
        return f"Reading guide at {self.position_y}px for {self.user.username} on {self.page_url}"


# User rewards and points tracking
class RewardSystem(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)
    level = models.IntegerField(default=1)
    streaks = models.IntegerField(default=0)  # Consecutive days of activity
    last_activity = models.DateField(null=True, blank=True)
    
    def update_streak(self):
        today = timezone.now().date()
        if self.last_activity:
            # If last activity was yesterday, increment streak
            yesterday = today - timezone.timedelta(days=1)
            if self.last_activity == yesterday:
                self.streaks += 1
            # If more than one day gap, reset streak
            elif self.last_activity < yesterday:
                self.streaks = 1
        else:
            # First activity
            self.streaks = 1
        
        self.last_activity = today
        self.save()
    
    def add_points(self, points_to_add):
        self.points += points_to_add
        
        # Level up if enough points (simple formula)
        points_needed = self.level * 100
        if self.points >= points_needed:
            self.level += 1
        
        self.save()
    
    def __str__(self):
        return f"Rewards for {self.user.username}: Level {self.level}, {self.points} points"


# Achievements and badges
class Achievement(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50)  # CSS class or icon identifier
    points_value = models.IntegerField(default=10)
    
    def __str__(self):
        return self.name


class UserAchievement(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    earned_date = models.DateTimeField(default=timezone.now)
    displayed = models.BooleanField(default=False)  # Whether shown to user
    
    class Meta:
        unique_together = ('user', 'achievement')
    
    def __str__(self):
        return f"{self.user.username} earned {self.achievement.name}"

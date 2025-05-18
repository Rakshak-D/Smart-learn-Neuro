from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse
from django.utils.text import slugify

# Subject choices
SUBJECT_CHOICES = [
    ('english', 'English'),
    ('math', 'Mathematics'),
    ('science', 'Science'),
    ('history', 'History'),
    ('geography', 'Geography'),
]

# Difficulty levels
DIFFICULTY_LEVELS = [
    ('beginner', 'Beginner'),
    ('intermediate', 'Intermediate'),
    ('advanced', 'Advanced'),
]

# Content types
CONTENT_TYPES = [
    ('text', 'Text'),
    ('video', 'Video'),
    ('audio', 'Audio'),
    ('interactive', 'Interactive'),
    ('game', 'Game'),
]

class Topic(models.Model):
    """Model to organize lessons into topics"""
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    subject = models.CharField(max_length=20, choices=SUBJECT_CHOICES, default='english')
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_LEVELS, default='beginner')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'title']
    
    def __str__(self):
        return f"{self.get_subject_display()}: {self.title}"

class Lesson(models.Model):
    """Model for storing lesson content with accessibility features"""
    # Basic information
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(blank=True)
    content = models.TextField(help_text="Main lesson content in Markdown format")
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='lessons')
    
    # Media and resources
    thumbnail = models.ImageField(upload_to='lesson_thumbnails/', null=True, blank=True)
    video_url = models.URLField(blank=True, null=True)
    audio_file = models.FileField(upload_to='lesson_audio/', null=True, blank=True)
    transcript = models.TextField(blank=True, help_text="Text transcript for audio/video content")
    
    # Metadata
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_LEVELS, default='beginner')
    duration = models.PositiveIntegerField(help_text="Duration in minutes", default=10)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES, default='text')
    
    # Accessibility features
    has_audio = models.BooleanField(default=False)
    has_video = models.BooleanField(default=False)
    has_transcript = models.BooleanField(default=False)
    has_interactive = models.BooleanField(default=False)
    has_quiz = models.BooleanField(default=False)
    
    # SEO and discoverability
    keywords = models.CharField(max_length=255, blank=True)
    is_published = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['topic__order', 'title']
        verbose_name = 'Lesson'
        verbose_name_plural = 'Lessons'
    
    def __str__(self):
        return f"{self.topic.title}: {self.title}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.topic.title}-{self.title}")
        if self.is_published and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('lesson_detail', kwargs={'slug': self.slug})
    
    def get_chunks(self, user=None, chunk_size=3):
        """
        Return lesson content as chunks based on user preferences.
        For users with ADHD or dyslexia, use smaller chunks.
        """
        if user and hasattr(user, 'learning_condition'):
            if user.learning_condition == 'ADHD':
                chunk_size = 2
            elif user.learning_condition == 'DYSLEXIA':
                chunk_size = 1
        
        paragraphs = self.content.split('\n\n')
        chunks = ['\n\n'.join(paragraphs[i:i + chunk_size]) 
                 for i in range(0, len(paragraphs), chunk_size)]
        return chunks
    
    def get_accessible_content(self, user=None):
        """Return content formatted based on user's accessibility needs"""
        content = self.content
        if user and hasattr(user, 'learning_condition'):
            if user.learning_condition == 'DYSLEXIC':
                # Add syllable breaks for dyslexic users
                content = self._add_syllable_breaks(content)
        return content
    
    def _add_syllable_breaks(self, text):
        """Add syllable breaks to text for better readability (simplified example)"""
        # This is a simplified example - in production, use a proper syllable breaking library
        return text  # Implement actual syllable breaking logic here
    
    def get_estimated_reading_time(self, user=None):
        """Return estimated reading time in minutes based on user's reading speed"""
        words_per_minute = 200  # Average reading speed
        if user and hasattr(user, 'reading_speed'):
            words_per_minute = user.reading_speed
        
        word_count = len(self.content.split())
        return max(1, round(word_count / words_per_minute))


class LessonResource(models.Model):
    """Additional resources for lessons (downloads, external links, etc.)"""
    RESOURCE_TYPES = [
        ('document', 'Document'),
        ('worksheet', 'Worksheet'),
        ('link', 'External Link'),
        ('audio', 'Audio File'),
        ('video', 'Video File'),
    ]
    
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='resources')
    title = models.CharField(max_length=200)
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES)
    file = models.FileField(upload_to='lesson_resources/', null=True, blank=True)
    url = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.lesson.title} - {self.title}"


class LessonProgress(models.Model):
    """Tracks user progress through lessons with detailed analytics"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='lesson_progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='user_progress')
    
    # Progress tracking
    is_started = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)
    completion_date = models.DateTimeField(null=True, blank=True)
    progress_percentage = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )
    
    # Time tracking
    time_spent = models.PositiveIntegerField(default=0)  # in seconds
    last_accessed = models.DateTimeField(auto_now=True)
    
    # Performance metrics
    quiz_score = models.FloatField(null=True, blank=True)  # Average score across all quizzes
    engagement_score = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    
    # User feedback
    difficulty_rating = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    notes = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Lesson Progress'
        verbose_name_plural = 'Lesson Progress'
        unique_together = ('user', 'lesson')
    
    def __str__(self):
        status = "Completed" if self.is_completed else "In Progress" if self.is_started else "Not Started"
        return f"{self.user.username} - {self.lesson.title} ({status} - {self.progress_percentage}%)"
    
    def update_progress(self, time_spent_seconds=0, increment_progress=0):
        """Update progress with time spent and optional progress increment"""
        self.time_spent += time_spent_seconds
        
        if increment_progress > 0:
            self.progress_percentage = min(100.0, self.progress_percentage + increment_progress)
            self.is_started = True
            
            if self.progress_percentage >= 100:
                self.is_completed = True
                self.completion_date = timezone.now()
                
        self.save()
        return self.progress_percentage
    
    def calculate_engagement_score(self, interactions):
        """Calculate engagement score based on user interactions"""
        # This is a simplified example - implement based on your metrics
        self.engagement_score = min(1.0, interactions * 0.1)  # Example calculation
        self.save()
        return self.engagement_score

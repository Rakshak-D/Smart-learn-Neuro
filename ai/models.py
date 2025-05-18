"""
Models for the AI app.
"""
import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()

# Constants
LEARNING_CONDITIONS = [
    ('NORMAL', 'Normal'),
    ('DYSLEXIA', 'Dyslexia'),
    ('ADHD', 'ADHD'),
    ('AUTISM', 'Autism Spectrum'),
    ('VISUAL_IMPAIRMENT', 'Visual Impairment'),
    ('HEARING_IMPAIRMENT', 'Hearing Impairment'),
]

CONTENT_TYPES = [
    ('TEXT', 'Text'),
    ('VIDEO', 'Video'),
    ('AUDIO', 'Audio'),
    ('INTERACTIVE', 'Interactive'),
    ('GAME', 'Educational Game'),
]

DIFFICULTY_LEVELS = [
    ('BEGINNER', 'Beginner'),
    ('INTERMEDIATE', 'Intermediate'),
    ('ADVANCED', 'Advanced'),
]

SESSION_STATUS = [
    ('NOT_STARTED', 'Not Started'),
    ('IN_PROGRESS', 'In Progress'),
    ('PAUSED', 'Paused'),
    ('COMPLETED', 'Completed'),
    ('ABANDONED', 'Abandoned'),
]

# Assessment types for different learning conditions
ASSESSMENT_TYPES = [
    ('DYSLEXIA', 'Dyslexia Assessment'),
    ('ADHD', 'ADHD Assessment'),
    ('ENGLISH', 'English Assessment'),
]

# Task types for different learning activities
TASK_TYPES = [
    ('MATCHING', 'Matching Task'),
    ('MULTIPLE_CHOICE', 'Multiple Choice'),
    ('SPELLING', 'Spelling Task'),
    ('LISTENING', 'Listening Task'),
    ('READING', 'Reading Task'),
    ('WRITING', 'Writing Task'),
]

class Topic(models.Model):
    """Learning topics for different subjects"""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    subject = models.CharField(max_length=100, default='English')
    level = models.CharField(
        max_length=20, 
        choices=DIFFICULTY_LEVELS, 
        default='BEGINNER'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    parent_topic = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='subtopics'
    )
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order', 'name']
        indexes = [
            models.Index(fields=['subject', 'level']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_level_display()})"
    
    @property
    def has_subtopics(self):
        """Check if the topic has subtopics."""
        return self.subtopics.exists()
    
    def get_absolute_url(self):
        """Get the URL for this topic."""
        from django.urls import reverse
        return reverse('topic-detail', kwargs={'pk': self.pk})

class LearningPath(models.Model):
    """Personalized learning paths for users"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='learning_paths'
    )
    name = models.CharField(max_length=200, default='My Learning Path')
    description = models.TextField(blank=True, null=True)
    topics = models.ManyToManyField(
        Topic, 
        through='LearningPathTopic',
        related_name='learning_paths'
    )
    current_topic = models.ForeignKey(
        Topic, 
        on_delete=models.SET_NULL, 
        null=True,
        blank=True,
        related_name='current_in_paths'
    )
    progress = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-is_active', '-updated_at']
        verbose_name = _('Learning Path')
        verbose_name_plural = _('Learning Paths')
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'name'], 
                name='unique_learning_path_name_per_user'
            )
        ]

    def __str__(self):
        return f"{self.user.username}'s {self.name}"
    
    def update_progress(self):
        """Update the progress of the learning path."""
        from django.db.models import Avg, Count, F, ExpressionWrapper, FloatField
        
        # Calculate progress based on completed topics
        progress_data = self.topics.aggregate(
            total=Count('id'),
            completed=Count('learningpathtopic', filter=models.Q(learningpathtopic__completed=True))
        )
        
        if progress_data['total'] > 0:
            self.progress = (progress_data['completed'] / progress_data['total']) * 100
        else:
            self.progress = 0.0
        
        # Mark as completed if all topics are completed
        if self.progress >= 100:
            self.is_active = False
            if not self.completed_at:
                self.completed_at = timezone.now()
        
        self.save()
        return self.progress
    
    def get_next_topic(self):
        """Get the next topic in the learning path."""
        if not self.current_topic:
            # Get the first topic in the path
            next_topic = self.learningpathtopic_set.filter(
                completed=False
            ).order_by('order').first()
            
            if next_topic:
                self.current_topic = next_topic.topic
                self.save()
                return self.current_topic
            return None
        
        # Get the current topic's order
        current_order = self.learningpathtopic_set.get(
            topic=self.current_topic
        ).order
        
        # Get the next topic in order
        next_topic = self.learningpathtopic_set.filter(
            order__gt=current_order,
            completed=False
        ).order_by('order').first()
        
        if next_topic:
            self.current_topic = next_topic.topic
            self.save()
            return self.current_topic
        
        # If no next topic, check if we should loop back to the start
        first_topic = self.learningpathtopic_set.order_by('order').first()
        if first_topic and first_topic.topic != self.current_topic:
            self.current_topic = first_topic.topic
            self.save()
            return self.current_topic
        
        return None

class LearningPathTopic(models.Model):
    """Mapping between learning paths and topics with additional data."""
    learning_path = models.ForeignKey(
        LearningPath, 
        on_delete=models.CASCADE
    )
    topic = models.ForeignKey(
        Topic, 
        on_delete=models.CASCADE
    )
    order = models.PositiveIntegerField(default=0)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['order']
        unique_together = ['learning_path', 'topic']
        verbose_name = _('Learning Path Topic')
        verbose_name_plural = _('Learning Path Topics')
    
    def __str__(self):
        return f"{self.learning_path.name} - {self.topic.name}"
    
    def save(self, *args, **kwargs):
        """Override save to update parent learning path progress."""
        is_new = self._state.adding
        
        # If marking as completed, set the completed_at timestamp
        if not is_new and 'completed' in kwargs.get('update_fields', []) and self.completed and not self.completed_at:
            self.completed_at = timezone.now()
        
        super().save(*args, **kwargs)
        
        # Update the learning path progress
        self.learning_path.update_progress()

class LearningSession(models.Model):
    """Tracks a user's learning session."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='learning_sessions'
    )
    learning_path = models.ForeignKey(
        LearningPath,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sessions'
    )
    current_topic = models.ForeignKey(
        Topic,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='active_sessions'
    )
    status = models.CharField(
        max_length=20,
        choices=SESSION_STATUS,
        default='NOT_STARTED'
    )
    progress = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.PositiveIntegerField(default=0)  # in seconds
    device_info = models.JSONField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    
    class Meta:
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status', 'start_time']),
        ]
    
    def __str__(self):
        return f"{self.user.username}'s session at {self.start_time}"
    
    def update_duration(self):
        """Update the session duration."""
        if self.status == 'IN_PROGRESS':
            self.duration_seconds = (timezone.now() - self.start_time).total_seconds()
            self.save(update_fields=['duration_seconds'])
        return self.duration_seconds
    
    def start(self):
        """Start the learning session."""
        if self.status == 'NOT_STARTED':
            self.status = 'IN_PROGRESS'
            self.start_time = timezone.now()
            self.save(update_fields=['status', 'start_time'])
            return True
        return False
    
    def pause(self):
        """Pause the learning session."""
        if self.status == 'IN_PROGRESS':
            self.status = 'PAUSED'
            self.update_duration()
            self.save(update_fields=['status', 'duration_seconds'])
            return True
        return False
    
    def resume(self):
        """Resume a paused learning session."""
        if self.status == 'PAUSED':
            self.status = 'IN_PROGRESS'
            # Reset start time to now to avoid counting paused time
            self.start_time = timezone.now() - timezone.timedelta(seconds=self.duration_seconds)
            self.save(update_fields=['status', 'start_time'])
            return True
        return False
    
    def complete(self):
        """Mark the learning session as completed."""
        if self.status in ['IN_PROGRESS', 'PAUSED']:
            self.status = 'COMPLETED'
            self.end_time = timezone.now()
            self.duration_seconds = (self.end_time - self.start_time).total_seconds()
            self.progress = 100.0
            self.save(update_fields=['status', 'end_time', 'duration_seconds', 'progress'])
            
            # Update the learning path progress if applicable
            if self.learning_path:
                self.learning_path.update_progress()
            
            return True
        return False
    
    def abandon(self, reason=None):
        """Mark the learning session as abandoned."""
        if self.status in ['IN_PROGRESS', 'PAUSED']:
            self.status = 'ABANDONED'
            self.end_time = timezone.now()
            self.duration_seconds = (self.end_time - self.start_time).total_seconds()
            
            if reason:
                if not hasattr(self, 'metadata'):
                    self.metadata = {}
                self.metadata['abandon_reason'] = str(reason)
            
            self.save(update_fields=['status', 'end_time', 'duration_seconds', 'metadata'])
            return True
        return False
    
    def update_progress(self, progress_percentage):
        """Update the progress of the learning session."""
        if 0 <= progress_percentage <= 100:
            self.progress = progress_percentage
            self.save(update_fields=['progress'])
            
            # If progress reaches 100%, mark as completed
            if progress_percentage >= 100:
                self.complete()
            
            return True
        return False
    
    def get_time_spent(self):
        """Get the total time spent in the session."""
        if self.status == 'IN_PROGRESS':
            return (timezone.now() - self.start_time).total_seconds()
        return self.duration_seconds or 0
    
    def get_average_pace(self):
        """Get the average pace of progress per minute."""
        time_spent_minutes = self.get_time_spent() / 60
        if time_spent_minutes > 0:
            return self.progress / time_spent_minutes
        return 0

class LearningAnalytics(models.Model):
    """Stores learning analytics data for users."""
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='learning_analytics'
    )
    date = models.DateField()
    time_spent_seconds = models.PositiveIntegerField(default=0)
    lessons_completed = models.PositiveIntegerField(default=0)
    assessments_completed = models.PositiveIntegerField(default=0)
    average_score = models.FloatField(null=True, blank=True)
    engagement_score = models.FloatField(default=0.0)
    focus_metric = models.FloatField(null=True, blank=True)
    mood = models.CharField(max_length=20, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Learning Analytics')
        verbose_name_plural = _('Learning Analytics')
        unique_together = ['user', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.user.username} - {self.date}"
    
    @classmethod
    def update_analytics(cls, user, date=None, **kwargs):
        """Update or create analytics for a user and date."""
        if date is None:
            date = timezone.now().date()
            
        analytics, created = cls.objects.get_or_create(
            user=user,
            date=date,
            defaults=kwargs
        )
        
        if not created:
            update_fields = []
            for field, value in kwargs.items():
                if hasattr(analytics, field):
                    setattr(analytics, field, value)
                    update_fields.append(field)
            
            if update_fields:
                analytics.save(update_fields=update_fields)
        
        return analytics, created
    
    @property
    def time_spent_formatted(self):
        """Return time spent in a human-readable format."""
        hours = self.time_spent_seconds // 3600
        minutes = (self.time_spent_seconds % 3600) // 60
        seconds = self.time_spent_seconds % 60
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        return f"{seconds}s"

class AIAssessment(models.Model):
    """AI Assessments for different learning conditions"""
    name = models.CharField(max_length=200)
    description = models.TextField()
    type = models.CharField(max_length=20, choices=ASSESSMENT_TYPES)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    difficulty = models.CharField(max_length=20)
    
    def __str__(self):
        return f"AI {self.name} ({self.type})"

class AssessmentQuestion(models.Model):
    """Questions for assessments"""
    assessment = models.ForeignKey(AIAssessment, on_delete=models.CASCADE)
    question_text = models.TextField()
    type = models.CharField(max_length=20, choices=TASK_TYPES)
    options = models.JSONField(null=True, blank=True)
    correct_answer = models.TextField()
    difficulty = models.CharField(max_length=20)
    
    def __str__(self):
        return self.question_text[:50] + "..."

class AssessmentResult(models.Model):
    """Results of user assessments"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    assessment = models.ForeignKey(AIAssessment, on_delete=models.CASCADE)
    score = models.FloatField()
    completed_at = models.DateTimeField(auto_now_add=True)
    answers = models.JSONField()
    feedback = models.TextField()
    
    def __str__(self):
        return f"{self.user.username} - {self.assessment.name} - {self.score}"

class LearningTask(models.Model):
    """Personalized learning tasks"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    type = models.CharField(max_length=20, choices=TASK_TYPES)
    content = models.TextField()
    difficulty = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    due_at = models.DateTimeField()
    completed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Task for {self.user.name} - {self.topic.name}"

class TaskPerformance(models.Model):
    """User performance on learning tasks"""
    task = models.ForeignKey(LearningTask, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    completion_time = models.DateTimeField()
    accuracy = models.FloatField()
    feedback = models.TextField()
    
    def __str__(self):
        return f"Performance for {self.task}"

class AdaptiveLearningProfile(models.Model):
    """Profile for adaptive learning"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    learning_style = models.CharField(max_length=50)
    engagement_level = models.FloatField(default=1.0)
    preferred_pace = models.FloatField(default=1.0)
    last_assessment_date = models.DateTimeField(null=True, blank=True)
    next_assessment_due = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Profile for {self.user.name}"

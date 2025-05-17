from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatSession(models.Model):
    """Represents a conversation session between a user and the chatbot"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_sessions')
    title = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    # Context for the conversation
    context = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"Chat with {self.user.username} - {self.title or 'New Chat'}"
    
    def save(self, *args, **kwargs):
        if not self.title and not self.pk:
            self.title = f"Chat {timezone.now().strftime('%Y-%m-%d %H:%M')}"
        super().save(*args, **kwargs)


class ChatMessage(models.Model):
    """Individual messages within a chat session"""
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    ]
    
    MESSAGE_TYPES = [
        ('text', 'Plain Text'),
        ('question', 'Question'),
        ('answer', 'Answer'),
        ('suggestion', 'Suggestion'),
        ('action', 'Action'),
    ]
    
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES, default='text')
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    
    # For tracking message relationships
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    
    # Metadata for learning and personalization
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.role}: {self.content[:50]}{'...' if len(self.content) > 50 else ''}"


class LearningPreference(models.Model):
    """Stores learning preferences for the chatbot to adapt its responses"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # Learning condition (ADHD, Dyslexia, etc.)
    learning_condition = models.CharField(
        max_length=20,
        choices=[
            ('ADHD', 'Attention Deficit Hyperactivity Disorder'),
            ('DYSLEXIA', 'Dyslexia'),
            ('NORMAL', 'No specific condition'),
            ('MIXED', 'Multiple conditions'),
        ],
        default='NORMAL'
    )
    
    # Response style preferences
    response_style = models.CharField(
        max_length=20,
        choices=[
            ('CONCISE', 'Short and to the point'),
            ('DETAILED', 'Detailed explanations'),
            ('STEP_BY_STEP', 'Step by step guidance'),
            ('VISUAL', 'Visual explanations'),
        ],
        default='CONCISE'
    )
    
    # Accessibility preferences
    prefer_audio = models.BooleanField(default=False)
    prefer_text = models.BooleanField(default=True)
    prefer_visuals = models.BooleanField(default=True)
    
    # ADHD-specific preferences
    enable_break_reminders = models.BooleanField(default=True)
    break_interval = models.PositiveIntegerField(default=25)  # minutes
    
    # Dyslexia-specific preferences
    preferred_font = models.CharField(max_length=50, default='Arial')
    font_size = models.PositiveIntegerField(default=16)  # px
    line_spacing = models.FloatField(default=1.5)
    
    # Updated timestamp
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Learning preferences for {self.user.username}"


class ChatbotKnowledgeBase(models.Model):
    """Stores knowledge base articles and responses for the chatbot"""
    title = models.CharField(max_length=200)
    content = models.TextField()
    tags = models.JSONField(default=list, blank=True)
    
    # For different learning conditions
    target_conditions = models.JSONField(default=list, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.title


class UserFeedback(models.Model):
    """Stores user feedback on chatbot responses"""
    FEEDBACK_TYPES = [
        ('POSITIVE', 'Positive'),
        ('NEGATIVE', 'Negative'),
        ('NEUTRAL', 'Neutral'),
        ('SUGGESTION', 'Suggestion'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE, related_name='feedbacks')
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPES)
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # For tracking improvements
    was_helpful = models.BooleanField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_feedback_type_display()} feedback from {self.user.username}"

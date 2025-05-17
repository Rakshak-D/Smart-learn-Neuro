from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

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
    description = models.TextField()
    subject = models.CharField(max_length=50, default='English')
    level = models.CharField(max_length=20)
    
    def __str__(self):
        return self.name

class LearningPath(models.Model):
    """Personalized learning paths for users"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    current_topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    progress = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Path for {self.user.name}"

class Assessment(models.Model):
    """Assessments for different learning conditions"""
    name = models.CharField(max_length=200)
    description = models.TextField()
    type = models.CharField(max_length=20, choices=ASSESSMENT_TYPES)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    difficulty = models.CharField(max_length=20)
    
    def __str__(self):
        return self.name

class AssessmentQuestion(models.Model):
    """Questions for assessments"""
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
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
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    score = models.FloatField()
    completed_at = models.DateTimeField(auto_now_add=True)
    answers = models.JSONField()
    feedback = models.TextField()
    
    def __str__(self):
        return f"{self.user.name} - {self.assessment.name}"

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

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.utils.text import slugify

# Question types
QUESTION_TYPES = [
    ('multiple_choice', 'Multiple Choice'),
    ('true_false', 'True/False'),
    ('fill_blank', 'Fill in the Blank'),
    ('matching', 'Matching'),
    ('short_answer', 'Short Answer'),
    ('essay', 'Essay'),
    ('audio_response', 'Audio Response'),
    ('drag_drop', 'Drag and Drop'),
]

# Difficulty levels
DIFFICULTY_LEVELS = [
    ('easy', 'Easy'),
    ('medium', 'Medium'),
    ('hard', 'Hard'),
]

class Assessment(models.Model):
    """
    Model representing an assessment with various question types and settings.
    Supports multiple question types, adaptive testing, and detailed analytics.
    """
    # Basic information
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(blank=True)
    instructions = models.TextField(blank=True)
    
    # Assessment settings
    time_limit = models.PositiveIntegerField(
        help_text="Time limit in minutes (0 for no limit)",
        default=0
    )
    passing_score = models.PositiveIntegerField(
        default=70,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    max_attempts = models.PositiveIntegerField(
        default=0,
        help_text="Maximum number of attempts allowed (0 for unlimited)"
    )
    is_active = models.BooleanField(default=True)
    is_adaptive = models.BooleanField(
        default=False,
        help_text="Whether the assessment adapts to user's skill level"
    )
    
    # Access control
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_assessments'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Assessment'
        verbose_name_plural = 'Assessments'
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def is_available(self):
        """Check if the assessment is currently available"""
        now = timezone.now()
        if not self.is_active:
            return False
        if self.start_date and now < self.start_date:
            return False
        if self.end_date and now > self.end_date:
            return False
        return True
    
    def get_questions_for_user(self, user):
        """Get questions for a specific user, considering adaptive testing"""
        questions = self.questions.filter(is_active=True)
        
        if self.is_adaptive and hasattr(user, 'learning_condition'):
            # For adaptive assessments, filter questions based on user's level
            difficulty = self._get_user_difficulty_level(user)
            questions = questions.filter(difficulty=difficulty)
            
        return questions.order_by('?')
    
    def _get_user_difficulty_level(self, user):
        """Determine appropriate difficulty level for adaptive testing"""
        # This is a simplified example - implement your adaptive logic here
        if user.learning_condition == 'DYSLEXIA':
            return 'easy'
        elif user.learning_condition == 'ADHD':
            return 'medium'
        return 'medium'


class Question(models.Model):
    """Model representing a question in an assessment"""
    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    question_text = models.TextField()
    question_type = models.CharField(
        max_length=20,
        choices=QUESTION_TYPES,
        default='multiple_choice'
    )
    difficulty = models.CharField(
        max_length=10,
        choices=DIFFICULTY_LEVELS,
        default='medium'
    )
    points = models.PositiveIntegerField(default=1)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return f"{self.assessment.title} - Question {self.order}"
    
    def get_answers(self):
        """Get all active answers for this question"""
        return self.answers.filter(is_correct=True)


class Answer(models.Model):
    """Model representing possible answers for a question"""
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='answers'
    )
    answer_text = models.TextField()
    is_correct = models.BooleanField(default=False)
    feedback = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.question.question_text[:50]} - {self.answer_text[:30]}"


class UserResponse(models.Model):
    """Model representing a user's response to an assessment"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assessment_responses'
    )
    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name='user_responses'
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='user_responses'
    )
    selected_answers = models.ManyToManyField(
        Answer,
        related_name='user_responses',
        blank=True
    )
    text_response = models.TextField(blank=True)
    audio_response = models.FileField(
        upload_to='audio_responses/',
        null=True,
        blank=True
    )
    is_correct = models.BooleanField(default=False)
    points_earned = models.FloatField(default=0)
    time_taken = models.PositiveIntegerField(
        help_text="Time taken to answer in seconds",
        default=0
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ('user', 'assessment', 'question')
    
    def __str__(self):
        return f"{self.user.username} - {self.assessment.title} - Q{self.question.id}"
    
    def calculate_score(self):
        """Calculate the score for this response"""
        if self.question.question_type in ['multiple_choice', 'true_false']:
            correct_answers = self.question.answers.filter(is_correct=True)
            selected_correct = self.selected_answers.filter(is_correct=True).count()
            
            if correct_answers.count() > 0:
                self.points_earned = (selected_correct / correct_answers.count()) * self.question.points
                self.is_correct = (selected_correct == correct_answers.count() and 
                                 self.selected_answers.count() == correct_answers.count())
        
        self.save()
        return self.points_earned


class AssessmentAttempt(models.Model):
    """Model to track a user's attempt at an assessment"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assessment_attempts'
    )
    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name='attempts'
    )
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    time_spent = models.PositiveIntegerField(default=0)  # in seconds
    score = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        null=True,
        blank=True
    )
    is_completed = models.BooleanField(default=False)
    is_passed = models.BooleanField(default=False)
    responses = models.ManyToManyField(
        UserResponse,
        related_name='attempts',
        blank=True
    )
    
    class Meta:
        ordering = ['-start_time']
    
    def __str__(self):
        return f"{self.user.username} - {self.assessment.title} - {self.start_time}"
    
    def calculate_score(self):
        """Calculate the overall score for this attempt"""
        if not self.is_completed:
            return None
            
        total_points = sum(r.points_earned for r in self.responses.all())
        max_possible = sum(r.question.points for r in self.responses.all())
        
        if max_possible > 0:
            self.score = (total_points / max_possible) * 100
            self.is_passed = self.score >= self.assessment.passing_score
            self.save()
            
        return self.score
    
    def complete_attempt(self):
        """Mark the attempt as complete and calculate final score"""
        if not self.is_completed:
            self.end_time = timezone.now()
            self.time_spent = (self.end_time - self.start_time).total_seconds()
            self.is_completed = True
            self.calculate_score()
            self.save()
            
            # Update user's learning analytics
            if hasattr(self.user, 'update_learning_analytics'):
                self.user.update_learning_analytics(
                    lesson_duration=self.time_spent // 60,
                    score=self.score
                )
        
        return self.score

"""
Serializers for the AI app.
"""
from rest_framework import serializers
from django.apps import apps

# Get models using string references to avoid circular imports
Lesson = apps.get_model('lessons', 'Lesson')
Topic = apps.get_model('lessons', 'Topic')
LessonProgress = apps.get_model('lessons', 'LessonProgress')
Assessment = apps.get_model('assessments', 'Assessment')
Question = apps.get_model('assessments', 'Question')
Answer = apps.get_model('assessments', 'Answer')
AssessmentAttempt = apps.get_model('assessments', 'AssessmentAttempt')
UserResponse = apps.get_model('assessments', 'UserResponse')
CustomUser = apps.get_model('users', 'CustomUser')


class TopicSerializer(serializers.ModelSerializer):
    """Serializer for Topic model."""
    class Meta:
        model = Topic
        fields = ['id', 'name', 'description', 'subject', 'is_active']
        read_only_fields = ['id']


class LessonSerializer(serializers.ModelSerializer):
    """Serializer for Lesson model with related topic."""
    topic = TopicSerializer(read_only=True)
    
    class Meta:
        model = Lesson
        fields = [
            'id', 'title', 'description', 'content', 'difficulty', 'duration', 
            'content_type', 'topic', 'thumbnail', 'video_url', 'transcript',
            'created_at', 'updated_at', 'is_published'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'content': {'write_only': True},  # Don't include full content in list views
        }


class LessonProgressSerializer(serializers.ModelSerializer):
    """Serializer for LessonProgress model."""
    lesson = LessonSerializer(read_only=True)
    
    class Meta:
        model = LessonProgress
        fields = [
            'id', 'user', 'lesson', 'is_completed', 'completion_percentage',
            'time_spent_seconds', 'last_accessed', 'feedback', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AnswerSerializer(serializers.ModelSerializer):
    """Serializer for Answer model."""
    class Meta:
        model = Answer
        fields = ['id', 'answer_text', 'is_correct', 'feedback', 'order']
        read_only_fields = ['id']


class QuestionSerializer(serializers.ModelSerializer):
    """Serializer for Question model with answers."""
    answers = AnswerSerializer(many=True, read_only=True)
    
    class Meta:
        model = Question
        fields = [
            'id', 'assessment', 'question_text', 'question_type', 'difficulty',
            'points', 'order', 'is_active', 'answers', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AssessmentSerializer(serializers.ModelSerializer):
    """Serializer for Assessment model with questions."""
    questions = QuestionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Assessment
        fields = [
            'id', 'title', 'description', 'instructions', 'time_limit', 'passing_score',
            'max_attempts', 'is_active', 'is_adaptive', 'start_date', 'end_date',
            'created_by', 'created_at', 'updated_at', 'questions'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserResponseSerializer(serializers.ModelSerializer):
    """Serializer for UserResponse model."""
    selected_answers = AnswerSerializer(many=True, read_only=True)
    
    class Meta:
        model = UserResponse
        fields = [
            'id', 'user', 'assessment', 'question', 'selected_answers',
            'text_response', 'audio_response', 'is_correct', 'points_earned',
            'time_taken', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class AssessmentAttemptSerializer(serializers.ModelSerializer):
    """Serializer for AssessmentAttempt model with user responses."""
    responses = UserResponseSerializer(many=True, read_only=True)
    
    class Meta:
        model = AssessmentAttempt
        fields = [
            'id', 'user', 'assessment', 'start_time', 'end_time', 'is_completed',
            'score', 'responses', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class UserLearningProfileSerializer(serializers.ModelSerializer):
    """Serializer for user learning profile data."""
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'learning_condition',
            'learning_style', 'difficulty_level', 'engagement_level', 'learning_streak',
            'total_learning_time', 'preferred_content_types', 'accessibility_settings',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class LearningAnalyticsSerializer(serializers.Serializer):
    """Serializer for learning analytics data."""
    total_learning_time = serializers.IntegerField()
    completion_rate = serializers.FloatField()
    lessons_completed = serializers.IntegerField()
    total_lessons = serializers.IntegerField()
    average_score = serializers.FloatField(allow_null=True)
    learning_streak = serializers.IntegerField()
    preferred_learning_style = serializers.CharField()
    
    activity_data = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField(),
            allow_empty=True
        )
    )
    
    next_recommendations = LessonSerializer(many=True)


class LearningPathStepSerializer(serializers.Serializer):
    """Serializer for a single step in a learning path."""
    type = serializers.CharField()
    title = serializers.CharField()
    description = serializers.CharField(required=False, allow_blank=True)
    duration = serializers.IntegerField(required=False)
    status = serializers.CharField(required=False)
    completed = serializers.BooleanField(required=False)
    
    def validate_type(self, value):
        """Validate that the type is one of the allowed values."""
        allowed_types = ['video', 'text', 'interactive', 'assessment', 'break', 'recommendation']
        if value not in allowed_types:
            raise serializers.ValidationError(f"Type must be one of {allowed_types}")
        return value


class LearningPathSerializer(serializers.Serializer):
    """Serializer for a complete learning path."""
    status = serializers.CharField()
    data = LearningPathStepSerializer(many=True)
    generated_at = serializers.DateTimeField()

"""
Serializers for AI API endpoints.
"""
from rest_framework import serializers

class TextSimilaritySerializer(serializers.Serializer):
    """Serializer for text similarity request."""
    text1 = serializers.CharField(required=True, max_length=10000)
    text2 = serializers.CharField(required=True, max_length=10000)

class KeywordExtractionSerializer(serializers.Serializer):
    """Serializer for keyword extraction request."""
    text = serializers.CharField(required=True, max_length=10000)
    top_n = serializers.IntegerField(default=10, min_value=1, max_value=50)

class SentimentAnalysisSerializer(serializers.Serializer):
    """Serializer for sentiment analysis request."""
    text = serializers.CharField(required=True, max_length=10000)

class EngagementAnalysisSerializer(serializers.Serializer):
    """Serializer for engagement analysis request."""
    video_frame = serializers.ImageField(required=False)
    interaction_data = serializers.DictField(
        required=False,
        child=serializers.FloatField(),
        default=dict
    )

class TextToSpeechSerializer(serializers.Serializer):
    """Serializer for text-to-speech request."""
    text = serializers.CharField(required=True, max_length=5000)
    voice = serializers.CharField(required=False, default='en-US')
    speed = serializers.FloatField(default=1.0, min_value=0.5, max_value=2.0)

class AdaptiveLearningRequestSerializer(serializers.Serializer):
    """Serializer for adaptive learning requests."""
    user_id = serializers.IntegerField(required=True)
    content_type = serializers.CharField(required=False, default='all')
    limit = serializers.IntegerField(default=5, min_value=1, max_value=20)

class LearningPathSerializer(serializers.Serializer):
    """Serializer for learning path generation."""
    user_id = serializers.IntegerField(required=True)
    topic_id = serializers.IntegerField(required=False)
    difficulty = serializers.ChoiceField(
        choices=['beginner', 'intermediate', 'advanced'],
        default='beginner'
    )
    duration_hours = serializers.FloatField(
        min_value=0.5,
        max_value=100,
        default=10.0
    )

class EngagementTrackingSerializer(serializers.Serializer):
    """Serializer for engagement tracking data."""
    user_id = serializers.IntegerField(required=True)
    session_id = serializers.CharField(required=True)
    timestamp = serializers.DateTimeField(required=True)
    event_type = serializers.CharField(required=True)
    event_data = serializers.DictField(required=False, default=dict)

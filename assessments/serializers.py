from rest_framework import serializers
from .models import Assessment, Response

class AssessmentSerializer(serializers.ModelSerializer):
    """
    Serializer for the Assessment model.
    Serializes the id, title, and audio_file fields.
    """
    class Meta:
        model = Assessment
        fields = ('id', 'title', 'audio_file')

class ResponseSerializer(serializers.ModelSerializer):
    """
    Serializer for the Response model.
    Serializes the id, user, assessment, and response_text fields.
    """
    class Meta:
        model = Response
        fields = ('id', 'user', 'assessment', 'response_text')

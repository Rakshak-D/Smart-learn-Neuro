from rest_framework import serializers
from .models import Lesson, LessonProgress

class LessonSerializer(serializers.ModelSerializer):
    """
    Serializer for the Lesson model.
    Serializes fields: id, title, content, image, audio_file.
    """
    class Meta:
        model = Lesson
        fields = ('id', 'title', 'content', 'image', 'audio_file')

class LessonProgressSerializer(serializers.ModelSerializer):
    """
    Serializer for the LessonProgress model.
    Serializes fields: id, user, lesson, progress.
    """
    class Meta:
        model = LessonProgress
        fields = ('id', 'user', 'lesson', 'progress')
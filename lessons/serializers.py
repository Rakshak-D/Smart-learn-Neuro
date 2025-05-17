from rest_framework import serializers
from .models import Lesson, LessonProgress

class LessonSerializer(serializers.ModelSerializer):
    """
    Serializer for the Lesson model.
    Serializes fields: id, title, content, and image.
    """
    class Meta:
        model = Lesson
        fields = ('id', 'title', 'content', 'image')

class LessonProgressSerializer(serializers.ModelSerializer):
    """
    Serializer for the LessonProgress model.
    Serializes fields: id, user, lesson, and progress.
    """
    class Meta:
        model = LessonProgress
        fields = ('id', 'user', 'lesson', 'progress')

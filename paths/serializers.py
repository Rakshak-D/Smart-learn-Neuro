from rest_framework import serializers
from .models import LearningPath, UserPath

class LearningPathSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearningPath
        fields = ('id', 'title', 'lessons')  # Serialize these fields for LearningPath

class UserPathSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPath
        fields = ('id', 'user', 'path', 'customized_order')  # Serialize these fields for UserPath

from rest_framework import serializers
from .models import CustomUser

# This serializer is used to convert CustomUser model instances
# to JSON format and vice versa (for use with Django REST Framework)
class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser  # Specifies the model to serialize
        fields = (
            'id',              # Unique ID of the user
            'username',        # Username of the user
            'font_size',       # User's preferred font size for UI accessibility
            'prefers_audio',   # Boolean: whether the user prefers audio-based learning
            'prefers_chunked'  # Boolean: whether the user prefers chunked content
        )

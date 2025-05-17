from rest_framework import serializers
from .models import (
    ChatSession, ChatMessage, 
    LearningPreference, UserFeedback,
    ChatbotKnowledgeBase
)


class ChatSessionSerializer(serializers.ModelSerializer):
    """Serializer for chat sessions"""
    message_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatSession
        fields = [
            'id', 'title', 'created_at', 'updated_at', 
            'is_active', 'message_count'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at', 'message_count']
    
    def get_message_count(self, obj):
        return obj.messages.count()


class ChatMessageSerializer(serializers.ModelSerializer):
    """Serializer for chat messages"""
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    message_type_display = serializers.CharField(source='get_message_type_display', read_only=True)
    
    class Meta:
        model = ChatMessage
        fields = [
            'id', 'session', 'role', 'role_display',
            'message_type', 'message_type_display', 'content',
            'created_at', 'parent', 'metadata'
        ]
        read_only_fields = ['created_at', 'metadata']


class LearningPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for learning preferences"""
    learning_condition_display = serializers.CharField(
        source='get_learning_condition_display', 
        read_only=True
    )
    response_style_display = serializers.CharField(
        source='get_response_style_display', 
        read_only=True
    )
    
    class Meta:
        model = LearningPreference
        fields = [
            'id', 'learning_condition', 'learning_condition_display',
            'response_style', 'response_style_display', 'prefer_audio',
            'prefer_text', 'prefer_visuals', 'enable_break_reminders',
            'break_interval', 'preferred_font', 'font_size', 'line_spacing',
            'updated_at'
        ]
        read_only_fields = ['user', 'updated_at']
    
    def validate_break_interval(self, value):
        if value < 5:
            raise serializers.ValidationError("Break interval must be at least 5 minutes.")
        if value > 120:
            raise serializers.ValidationError("Break interval cannot exceed 120 minutes.")
        return value
    
    def validate_font_size(self, value):
        if value < 10:
            raise serializers.ValidationError("Font size must be at least 10px.")
        if value > 36:
            raise serializers.ValidationError("Font size cannot exceed 36px.")
        return value


class UserFeedbackSerializer(serializers.ModelSerializer):
    """Serializer for user feedback"""
    feedback_type_display = serializers.CharField(
        source='get_feedback_type_display',
        read_only=True
    )
    
    class Meta:
        model = UserFeedback
        fields = [
            'id', 'message', 'feedback_type', 'feedback_type_display',
            'comments', 'was_helpful', 'created_at'
        ]
        read_only_fields = ['user', 'created_at']


class ChatbotKnowledgeBaseSerializer(serializers.ModelSerializer):
    """Serializer for chatbot knowledge base"""
    class Meta:
        model = ChatbotKnowledgeBase
        fields = [
            'id', 'title', 'content', 'tags',
            'target_conditions', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

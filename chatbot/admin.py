import json
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    ChatSession, ChatMessage, 
    LearningPreference, UserFeedback,
    ChatbotKnowledgeBase
)


class ChatMessageInline(admin.TabularInline):
    """Inline admin for chat messages"""
    model = ChatMessage
    fields = ('role', 'message_type', 'content_preview', 'created_at')
    readonly_fields = ('content_preview', 'created_at')
    extra = 0
    
    def content_preview(self, obj):
        """Show a preview of the message content"""
        preview = obj.content[:50]
        if len(obj.content) > 50:
            preview += '...'
        return preview
    content_preview.short_description = 'Content Preview'


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    """Admin for chat sessions"""
    list_display = ('id', 'user', 'title', 'message_count', 'created_at', 'updated_at', 'is_active')
    list_filter = ('is_active', 'created_at', 'updated_at')
    search_fields = ('user__username', 'title', 'id')
    readonly_fields = ('created_at', 'updated_at', 'context_preview')
    inlines = [ChatMessageInline]
    
    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = 'Messages'
    
    def context_preview(self, obj):
        """Show a formatted preview of the context"""
        if not obj.context:
            return "No context available"
        return format_html('<pre>{}</pre>', json.dumps(obj.context, indent=2))
    context_preview.short_description = 'Context (JSON)'


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    """Admin for chat messages"""
    list_display = ('id', 'session', 'role', 'message_type', 'content_preview', 'created_at')
    list_filter = ('role', 'message_type', 'created_at')
    search_fields = ('content', 'session__id', 'session__user__username')
    readonly_fields = ('created_at', 'metadata_preview')
    
    def content_preview(self, obj):
        """Show a preview of the message content"""
        preview = obj.content[:50]
        if len(obj.content) > 50:
            preview += '...'
        return preview
    content_preview.short_description = 'Content'
    
    def metadata_preview(self, obj):
        """Show a formatted preview of the metadata"""
        if not obj.metadata:
            return "No metadata available"
        return format_html('<pre>{}</pre>', json.dumps(obj.metadata, indent=2))
    metadata_preview.short_description = 'Metadata (JSON)'


@admin.register(LearningPreference)
class LearningPreferenceAdmin(admin.ModelAdmin):
    """Admin for learning preferences"""
    list_display = ('user', 'learning_condition', 'response_style', 'updated_at')
    list_filter = ('learning_condition', 'response_style')
    search_fields = ('user__username',)
    readonly_fields = ('updated_at',)


@admin.register(UserFeedback)
class UserFeedbackAdmin(admin.ModelAdmin):
    """Admin for user feedback"""
    list_display = ('user', 'feedback_type', 'was_helpful', 'created_at')
    list_filter = ('feedback_type', 'was_helpful', 'created_at')
    search_fields = ('user__username', 'comments', 'message__content')
    readonly_fields = ('created_at',)


@admin.register(ChatbotKnowledgeBase)
class ChatbotKnowledgeBaseAdmin(admin.ModelAdmin):
    """Admin for chatbot knowledge base"""
    list_display = ('title', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'created_at', 'updated_at')
    search_fields = ('title', 'content', 'tags')
    readonly_fields = ('created_at', 'updated_at', 'target_conditions_list')
    
    def target_conditions_list(self, obj):
        """Display target conditions as a list"""
        if not obj.target_conditions:
            return "No specific conditions"
        return ", ".join(obj.target_conditions)
    target_conditions_list.short_description = 'Target Conditions'

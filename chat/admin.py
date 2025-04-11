from django.contrib import admin
from .models import Conversation, Message, AIResponse

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('title', 'conversation_type', 'initiator', 'receiver', 'created_at', 'is_active')
    list_filter = ('conversation_type', 'is_active', 'created_at')
    search_fields = ('title', 'initiator__username', 'receiver__username')
    date_hierarchy = 'created_at'

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('conversation', 'sender', 'message_type', 'timestamp', 'is_read')
    list_filter = ('message_type', 'is_read', 'timestamp')
    search_fields = ('content', 'sender__username')
    date_hierarchy = 'timestamp'

@admin.register(AIResponse)
class AIResponseAdmin(admin.ModelAdmin):
    list_display = ('message', 'response_time', 'feedback')
    list_filter = ('feedback',)

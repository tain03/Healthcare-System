from django.db import models
from django.conf import settings
from django.utils import timezone

class Conversation(models.Model):
    CONVERSATION_TYPES = (
        ('patient_doctor', 'Patient-Doctor'),
        ('patient_support', 'Patient-Support'),
        ('doctor_support', 'Doctor-Support'),
        ('ai_assistant', 'AI Assistant'),
    )

    title = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    conversation_type = models.CharField(max_length=20, choices=CONVERSATION_TYPES)
    is_active = models.BooleanField(default=True)

    # Participants
    initiator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='initiated_conversations')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_conversations', null=True, blank=True)

    def __str__(self):
        return f"{self.title} ({self.get_conversation_type_display()})"

    def get_last_message(self):
        return self.messages.order_by('-timestamp').first()

    def get_unread_count(self, user):
        return self.messages.filter(is_read=False).exclude(sender=user).count()

class Message(models.Model):
    MESSAGE_TYPES = (
        ('text', 'Text'),
        ('image', 'Image'),
        ('file', 'File'),
        ('ai_response', 'AI Response'),
    )

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages', null=True, blank=True)
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='text')
    attachment = models.FileField(upload_to='chat_attachments/', null=True, blank=True)

    def __str__(self):
        sender_name = self.sender.get_full_name() if self.sender else "AI Assistant"
        return f"Message from {sender_name} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        ordering = ['timestamp']

class AIResponse(models.Model):
    message = models.OneToOneField(Message, on_delete=models.CASCADE, related_name='ai_response')
    prompt = models.TextField()
    response_time = models.FloatField(help_text="Response time in seconds")
    feedback = models.IntegerField(null=True, blank=True, help_text="User rating from 1-5")

    def __str__(self):
        return f"AI Response for {self.message}"

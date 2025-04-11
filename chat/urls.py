from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.chat_home, name='home'),
    path('conversation/<int:conversation_id>/', views.conversation_detail, name='conversation'),
    path('create/', views.create_conversation, name='create_conversation'),
    path('send/<int:conversation_id>/', views.send_message, name='send_message'),
    path('get-messages/<int:conversation_id>/', views.get_messages, name='get_messages'),
    path('rate/<int:message_id>/', views.rate_ai_response, name='rate_ai_response'),
    path('unread-count/', views.get_unread_count, name='unread_count'),
]

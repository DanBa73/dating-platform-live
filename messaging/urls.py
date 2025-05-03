# messaging/urls.py (Verschleierte URLs für mehr Sicherheit)
from django.urls import path
# Benötigte Views importieren
from . import views
from .views import (
    AISuggestionView, 
    ConversationAiSettingsDetailView, 
    MessageAttachmentUploadView,
    EnhancedAISuggestionView
)

app_name = 'messaging'

urlpatterns = [
    # Normale User APIs
    path('send/', views.send_message_view, name='send_message'),
    path('conversation/<int:other_user_id>/', views.get_conversation_view, name='get_conversation'),

    # Verschleierte Moderator APIs
    path('secure/managed-chats/', views.list_moderator_conversations, name='list_moderator_conversations'),
    path('secure/chat-session/<int:real_user_id>/<int:fake_user_id>/',
         views.get_moderator_conversation_view,
         name='get_moderator_conversation'),
    path('secure/response/',
         views.moderator_reply_view,
         name='moderator_reply'),

    # APIs für normale Benutzer
    path('conversations/', views.list_user_conversations, name='list_user_conversations'),
    
    # Verschleierte APIs für Assistenz-Funktionen
    path('enhanced-reply-suggestions/', AISuggestionView.as_view(), name='ai_suggest_reply'),
    path('advanced-reply-options/', EnhancedAISuggestionView.as_view(), name='enhanced_ai_suggest_reply'),
    path('chat-preferences/<int:real_user_id>/<int:fake_user_id>/',
         ConversationAiSettingsDetailView.as_view(),
         name='conversation_ai_settings_detail'),

    # URLs für Nachrichtenanhänge
    path('upload-attachment/', MessageAttachmentUploadView.as_view(), name='upload_attachment'),
    path('conversation-with-attachments/<int:other_user_id>/', 
         views.get_conversation_with_attachments_view, 
         name='get_conversation_with_attachments'),
]
# Ende der Datei messaging/urls.py

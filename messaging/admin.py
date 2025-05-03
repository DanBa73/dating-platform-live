# messaging/admin.py (Mit Konversationsübersicht, MessageAttachment und Massennachrichten)

from django.contrib import admin
from django.utils.html import format_html
from django.urls import path, reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.db.models import Count, Max, Q
from django.contrib.admin.views.main import ChangeList

from .models import Message, ConversationAiSettings, MessageAttachment
from accounts.models import CustomUser
from .views_mass_message import mass_message_form, mass_message_preview, mass_message_send

# Register your models here.

# Optional: Admin für das Message Modell (falls du Nachrichten im Admin sehen willst)
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'timestamp', 'is_read', 'content_preview')
    list_filter = ('timestamp', 'is_read')
    search_fields = ('sender__username', 'recipient__username', 'content')
    readonly_fields = ('timestamp',) # Normalerweise nicht änderbar

    def content_preview(self, obj):
        # Zeigt eine Vorschau des Inhalts an
        return obj.content[:50] + ('...' if len(obj.content) > 50 else '')
    content_preview.short_description = 'Content Preview'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('mass_message/', 
                 self.admin_site.admin_view(mass_message_form), 
                 name='mass_message_form'),
            path('mass_message_preview/', 
                 self.admin_site.admin_view(mass_message_preview), 
                 name='mass_message_preview'),
            path('mass_message_send/', 
                 self.admin_site.admin_view(mass_message_send), 
                 name='mass_message_send'),
        ]
        return custom_urls + urls
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['mass_message_url'] = reverse('admin:mass_message_form')
        return super().changelist_view(request, extra_context=extra_context)


# --- NEU: Admin-Konfiguration für ConversationAiSettings ---
@admin.register(ConversationAiSettings)
class ConversationAiSettingsAdmin(admin.ModelAdmin):
    """
    Admin-Interface für die AI-Einstellungen pro Konversation.
    """
    list_display = ('real_user', 'fake_user', 'ai_mode', 'updated_at') # Welche Spalten anzeigen?
    list_filter = ('ai_mode', 'fake_user') # Wonach filtern?
    search_fields = ('real_user__username', 'fake_user__username') # Suche nach Usernamen
    list_editable = ('ai_mode',) # Erlaube schnelles Ändern des Modus in der Liste
    list_per_page = 50 # Wie viele Einträge pro Seite
    readonly_fields = ('created_at', 'updated_at') # Diese Felder nicht bearbeitbar machen
    # Wichtig bei vielen Usern: raw_id_fields statt Dropdown für User-Auswahl
    raw_id_fields = ('real_user', 'fake_user')
    # Sortierung (optional)
    # ordering = ('-updated_at',) # Ist schon im Model Meta definiert

    # --- NEU: Link zur Konversationsübersicht hinzufügen ---
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('conversation_overview/', 
                 self.admin_site.admin_view(self.conversation_overview), 
                 name='conversation_overview'),
            path('update_ai_mode/', 
                 self.admin_site.admin_view(self.update_ai_mode), 
                 name='update_ai_mode'),
        ]
        return custom_urls + urls
    
    def conversation_overview(self, request):
        """
        Zeigt eine Übersicht aller Konversationen zwischen echten und Fake-Benutzern.
        """
        # Alle Konversationen zwischen echten und Fake-Benutzern abrufen
        conversations = []
        
        # Alle Fake-Benutzer abrufen
        fake_users = CustomUser.objects.filter(is_fake=True)
        
        # Für jeden Fake-Benutzer die Konversationen mit echten Benutzern abrufen
        for fake_user in fake_users:
            # Echte Benutzer finden, mit denen der Fake-Benutzer kommuniziert hat
            real_users = CustomUser.objects.filter(
                Q(sent_messages__recipient=fake_user) | Q(received_messages__sender=fake_user),
                is_fake=False
            ).distinct()
            
            for real_user in real_users:
                # Anzahl der Nachrichten in der Konversation
                message_count = Message.objects.filter(
                    (Q(sender=fake_user) & Q(recipient=real_user)) | 
                    (Q(sender=real_user) & Q(recipient=fake_user))
                ).count()
                
                # Letzte Nachricht in der Konversation
                last_message = Message.objects.filter(
                    (Q(sender=fake_user) & Q(recipient=real_user)) | 
                    (Q(sender=real_user) & Q(recipient=fake_user))
                ).order_by('-timestamp').first()
                
                # KI-Einstellungen für diese Konversation
                ai_settings, created = ConversationAiSettings.objects.get_or_create(
                    real_user=real_user,
                    fake_user=fake_user,
                    defaults={'ai_mode': ConversationAiSettings.AiMode.NONE}
                )
                
                conversations.append({
                    'real_user': real_user,
                    'fake_user': fake_user,
                    'message_count': message_count,
                    'last_message': last_message,
                    'ai_settings': ai_settings,
                    'ai_mode': ai_settings.ai_mode,
                    'ai_mode_display': ai_settings.get_ai_mode_display(),
                })
        
        # Nach letzter Nachricht sortieren
        conversations.sort(key=lambda x: x['last_message'].timestamp if x['last_message'] else None, reverse=True)
        
        # AI-Modi für das Formular
        ai_modes = [
            {'value': mode[0], 'display': mode[1]} 
            for mode in ConversationAiSettings.AiMode.choices
        ]
        
        context = {
            'title': 'Konversationsübersicht',
            'conversations': conversations,
            'ai_modes': ai_modes,
            **admin.site.each_context(request),
        }
        
        return render(request, 'admin/messaging/conversation/change_list.html', context)
    
    def update_ai_mode(self, request):
        """
        Aktualisiert den KI-Modus für eine Konversation.
        """
        if request.method == 'POST':
            real_user_id = request.POST.get('real_user_id')
            fake_user_id = request.POST.get('fake_user_id')
            ai_mode = request.POST.get('ai_mode')
            
            if real_user_id and fake_user_id and ai_mode:
                real_user = CustomUser.objects.get(id=real_user_id)
                fake_user = CustomUser.objects.get(id=fake_user_id)
                
                ai_settings, created = ConversationAiSettings.objects.get_or_create(
                    real_user=real_user,
                    fake_user=fake_user,
                    defaults={'ai_mode': ConversationAiSettings.AiMode.NONE}
                )
                
                ai_settings.ai_mode = ai_mode
                ai_settings.save()
                
                self.message_user(
                    request, 
                    f"KI-Modus für Konversation zwischen {real_user.username} und {fake_user.username} auf {ai_settings.get_ai_mode_display()} geändert."
                )
        
        return HttpResponseRedirect(reverse('admin:conversation_overview'))
    
    # --- NEU: Link zur Konversationsübersicht in der Changelist-Seite hinzufügen ---
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['conversation_overview_url'] = reverse('admin:conversation_overview')
        return super().changelist_view(request, extra_context=extra_context)

# --- Admin-Konfiguration für MessageAttachment ---
@admin.register(MessageAttachment)
class MessageAttachmentAdmin(admin.ModelAdmin):
    """
    Admin-Interface für Nachrichtenanhänge.
    """
    list_display = ('message_info', 'file_preview', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('message__sender__username', 'message__recipient__username')
    readonly_fields = ('uploaded_at', 'file_preview')
    
    def message_info(self, obj):
        """Zeigt Informationen über die zugehörige Nachricht an."""
        return f"Von {obj.message.sender.username} an {obj.message.recipient.username}"
    message_info.short_description = 'Nachricht'
    
    def file_preview(self, obj):
        """Zeigt eine Vorschau des Bildes an."""
        if obj.file:
            return format_html('<img src="{}" width="100" height="auto" />', obj.file.url)
        return "Kein Bild"
    file_preview.short_description = 'Vorschau'

# Ende der Datei messaging/admin.py

# messaging/models.py (Mit ConversationAiSettings und MessageAttachment)
from django.conf import settings # Um auf AUTH_USER_MODEL zugreifen zu können
from django.db import models
from django.utils.translation import gettext_lazy as _ # Für Choices-Texte
import os

# --- Message Model (unverändert) ---
class Message(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='sent_messages',
        on_delete=models.CASCADE
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='received_messages',
        on_delete=models.CASCADE
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"From {self.sender.username} to {self.recipient.username} at {self.timestamp:%Y-%m-%d %H:%M}"

    class Meta:
        ordering = ['timestamp']

# --- NEU: Modell für AI-Einstellungen pro Konversation ---
class ConversationAiSettings(models.Model):
    """
    Speichert den AI-Modus für eine spezifische Konversation
    zwischen einem echten User und einem Fake User.
    """
    # Choices für das ai_mode Feld
    class AiMode(models.TextChoices):
        NONE = 'NONE', _('No AI Support')
        ASSISTED = 'ASSISTED', _('AI Assisted Replies')
        AUTO = 'AUTO', _('AI Automatic Replies')

    real_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, # Wenn User gelöscht, Einstellung löschen
        related_name='ai_settings_as_real_user',
        limit_choices_to={'is_fake': False}, # Stellt sicher, dass es ein echter User ist
        verbose_name=_('Real User')
    )
    fake_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, # Wenn User gelöscht, Einstellung löschen
        related_name='ai_settings_as_fake_user',
        limit_choices_to={'is_fake': True}, # Stellt sicher, dass es ein Fake User ist
        verbose_name=_('Fake User')
    )
    ai_mode = models.CharField(
        max_length=10,
        choices=AiMode.choices,
        default=AiMode.NONE, # Standardmäßig keine AI
        verbose_name=_('AI Mode'),
        help_text=_('Select the AI operation mode for this specific conversation.')
    )
    # Optional: Zeitstempel für Erstellung/Änderung
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Conversation AI Setting')
        verbose_name_plural = _('Conversation AI Settings')
        # Stellt sicher, dass es nur einen Eintrag pro User-Paar gibt
        constraints = [
            models.UniqueConstraint(fields=['real_user', 'fake_user'], name='unique_ai_setting_per_conversation')
        ]
        ordering = ['-updated_at'] # Neueste Änderungen zuerst anzeigen

    def __str__(self):
        return f"AI Settings for {self.real_user.username} <-> {self.fake_user.username}: {self.get_ai_mode_display()}"

# --- ENDE NEU ---

def message_attachment_path(instance, filename):
    """
    Generiert den Dateipfad für hochgeladene Nachrichtenanhänge.
    Format: message_attachments/user_<user_id>/<timestamp>_<filename>
    """
    # Extrahiere Dateiendung
    ext = filename.split('.')[-1]
    # Erstelle neuen Dateinamen mit Zeitstempel
    new_filename = f"{instance.message.timestamp.strftime('%Y%m%d%H%M%S')}_{instance.message.id}.{ext}"
    # Rückgabe des Pfads
    return os.path.join('message_attachments', f"user_{instance.message.sender.id}", new_filename)

class MessageAttachment(models.Model):
    """
    Speichert Dateianhänge (Bilder) für Nachrichten.
    """
    message = models.ForeignKey(
        Message,
        related_name='attachments',
        on_delete=models.CASCADE,
        verbose_name=_('Message')
    )
    file = models.ImageField(
        upload_to=message_attachment_path,
        verbose_name=_('Image File'),
        help_text=_('Upload an image to attach to this message.')
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Message Attachment')
        verbose_name_plural = _('Message Attachments')
        ordering = ['uploaded_at']
    
    def __str__(self):
        return f"Attachment for message {self.message.id} from {self.message.sender.username}"
    
    @property
    def filename(self):
        return os.path.basename(self.file.name)

# Ende der Datei messaging/models.py

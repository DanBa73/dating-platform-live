# messaging/serializers.py (Mit ConversationAiSettingsSerializer und MessageAttachmentSerializer)

from rest_framework import serializers
from accounts.models import CustomUser # Importiere CustomUser direkt
# Modelle importieren
from .models import Message, ConversationAiSettings, MessageAttachment
from django.conf import settings
from accounts.serializers import PublicUserSerializer

# --- UserSerializer (mit profile_picture_url und zusätzlichen Feldern) ---
class UserSerializer(serializers.ModelSerializer):
    profile_picture_url = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'is_fake', 'profile_picture_url', 'birth_date', 'city', 'state', 'country', 'about_me', 'gender', 'seeking', 'age']
    
    def get_age(self, obj):
        if obj.birth_date:
            try:
                from django.utils import timezone
                today = timezone.now().date()
                # Korrekte Altersberechnung
                age = today.year - obj.birth_date.year - ((today.month, today.day) < (obj.birth_date.month, obj.birth_date.day))
                return age if age >= 0 else None # Gebe Alter zurück (oder None wenn negativ)
            except Exception:
                # Bei unerwarteten Fehlern (z.B. ungültiges Datum)
                return None
        return None # Kein Alter, wenn kein Geburtsdatum
    
    def get_profile_picture_url(self, obj):
        first_approved_image = obj.profile_images.filter(is_approved=True).order_by('uploaded_at').first()
        if first_approved_image and hasattr(first_approved_image.image, 'url'):
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(first_approved_image.image.url)
            else:
                try:
                    media_url = getattr(settings, 'MEDIA_URL', '/media/')
                    return f"{media_url}{first_approved_image.image.name}"
                except Exception:
                    return None
        return None

# --- MessageSerializer (für Moderatoren) ---
class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    recipient = UserSerializer(read_only=True)
    class Meta:
        model = Message
        fields = ['id', 'sender', 'recipient', 'content', 'timestamp', 'is_read']

# --- PublicMessageSerializer (für echte Benutzer) ---
class PublicMessageSerializer(serializers.ModelSerializer):
    """
    Serializer für Nachrichten, der an echte Benutzer gesendet wird.
    Verwendet PublicUserSerializer, um sensible Informationen zu verbergen.
    """
    sender = PublicUserSerializer(read_only=True)
    recipient = PublicUserSerializer(read_only=True)
    
    class Meta:
        model = Message
        fields = ['id', 'sender', 'recipient', 'content', 'timestamp', 'is_read']

# --- ModeratorConversationSerializer (unverändert) ---
class ModeratorConversationSerializer(serializers.Serializer):
    real_user = UserSerializer(read_only=True)
    fake_user = UserSerializer(read_only=True)
    last_message_content = serializers.CharField(read_only=True, max_length=100)
    last_message_timestamp = serializers.DateTimeField(read_only=True)


# --- NEU: Serializer für Conversation AI Settings ---
class ConversationAiSettingsSerializer(serializers.ModelSerializer):
    """
    Serializer, der nur den AI-Modus einer Konversationseinstellung zurückgibt.
    """
    class Meta:
        model = ConversationAiSettings
        fields = ['ai_mode'] # Wir brauchen nur dieses Feld für die Frontend-Logik
        # Da wir diesen Serializer nur zum Lesen verwenden, sind keine weiteren Angaben nötig.
# --- ENDE NEU ---

# --- MessageAttachmentSerializer ---
class MessageAttachmentSerializer(serializers.ModelSerializer):
    """
    Serializer für Nachrichtenanhänge (Bilder).
    """
    file_url = serializers.SerializerMethodField()
    file_type = serializers.SerializerMethodField()
    
    class Meta:
        model = MessageAttachment
        fields = ['id', 'file', 'file_url', 'file_type', 'uploaded_at']
        read_only_fields = ['uploaded_at']
    
    def get_file_url(self, obj):
        """Gibt die vollständige URL des Bildes zurück."""
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            else:
                try:
                    media_url = getattr(settings, 'MEDIA_URL', '/media/')
                    return f"{media_url}{obj.file.name}"
                except Exception:
                    return None
        return None
    
    def get_file_type(self, obj):
        """Gibt den MIME-Typ der Datei zurück."""
        if obj.file:
            # Extrahiere die Dateiendung
            filename = obj.file.name
            ext = filename.split('.')[-1].lower()
            
            # Ordne Dateiendungen MIME-Typen zu
            mime_types = {
                'jpg': 'image/jpeg',
                'jpeg': 'image/jpeg',
                'png': 'image/png',
                'gif': 'image/gif',
                'webp': 'image/webp',
                'svg': 'image/svg+xml',
                'bmp': 'image/bmp'
            }
            
            return mime_types.get(ext, 'application/octet-stream')
        return 'application/octet-stream'

# --- MessageSerializer mit Anhängen ---
class MessageWithAttachmentsSerializer(MessageSerializer):
    """
    Erweitert den MessageSerializer um Anhänge.
    """
    attachments = MessageAttachmentSerializer(many=True, read_only=True)
    
    class Meta(MessageSerializer.Meta):
        fields = MessageSerializer.Meta.fields + ['attachments']

# --- PublicMessageSerializer mit Anhängen ---
class PublicMessageWithAttachmentsSerializer(PublicMessageSerializer):
    """
    Erweitert den PublicMessageSerializer um Anhänge.
    Wird für echte Benutzer verwendet, um sensible Informationen zu verbergen.
    """
    attachments = MessageAttachmentSerializer(many=True, read_only=True)
    
    class Meta(PublicMessageSerializer.Meta):
        fields = PublicMessageSerializer.Meta.fields + ['attachments']

# Ende der Datei messaging/serializers.py

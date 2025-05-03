# messaging/views.py (Letzter Versuch - Korrekte Einrückung überall geprüft)
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.db.models import Q, Max, F, Case, When, BooleanField
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
import openai
from .models import Message, ConversationAiSettings, MessageAttachment
from accounts.models import CustomUser
from .serializers import (
    MessageSerializer,
    PublicMessageSerializer,
    ModeratorConversationSerializer,
    ConversationAiSettingsSerializer,
    MessageWithAttachmentsSerializer,
    PublicMessageWithAttachmentsSerializer,
    MessageAttachmentSerializer
)
from rest_framework.parsers import MultiPartParser, FormParser

# --- Konstante für Chat-Historie ---
CONVERSATION_HISTORY_LENGTH = 15

# --- send_message_view ---
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_message_view(request):
    sender = request.user
    recipient_id = request.data.get('recipient_id')
    content = request.data.get('content')
    if not recipient_id: return Response({"error": "Recipient ID is required."}, status=status.HTTP_400_BAD_REQUEST)
    if not content or not content.strip(): return Response({"error": "Message content cannot be empty."}, status=status.HTTP_400_BAD_REQUEST)
    try: recipient_id_int = int(recipient_id)
    except (ValueError, TypeError): return Response({"error": "Invalid Recipient ID format."}, status=status.HTTP_400_BAD_REQUEST)
    if sender.id == recipient_id_int: return Response({"error": "You cannot send a message to yourself."}, status=status.HTTP_400_BAD_REQUEST)
    try: recipient = CustomUser.objects.get(pk=recipient_id_int)
    except CustomUser.DoesNotExist: return Response({"error": "Recipient not found."}, status=status.HTTP_404_NOT_FOUND)
    MESSAGE_COST = 5
    if sender.coin_balance >= MESSAGE_COST:
        message = Message.objects.create(sender=sender, recipient=recipient, content=content)
        sender.coin_balance -= MESSAGE_COST; sender.save(update_fields=['coin_balance'])
        return Response({"message": "Message sent successfully.", "id": message.id}, status=status.HTTP_201_CREATED)
    else: return Response({"error": "Insufficient coins."}, status=status.HTTP_402_PAYMENT_REQUIRED)

# --- get_conversation_view ---
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_conversation_view(request, other_user_id):
    user = request.user
    try: other_user = CustomUser.objects.get(pk=other_user_id)
    except (CustomUser.DoesNotExist, ValueError, TypeError): return Response({"error": "Invalid or non-existent other_user_id."}, status=status.HTTP_404_NOT_FOUND)
    if user.id == other_user_id: return Response({"error": "Cannot retrieve conversation with yourself."}, status=status.HTTP_400_BAD_REQUEST)
    messages = Message.objects.filter( (Q(sender=user) & Q(recipient=other_user)) | (Q(sender=other_user) & Q(recipient=user)) ).select_related('sender', 'recipient').order_by('timestamp')
    
    # Verwende PublicMessageSerializer für echte Benutzer, MessageSerializer für Moderatoren
    if user.is_staff:
        serializer = MessageSerializer(messages, many=True, context={'request': request})
    else:
        serializer = PublicMessageSerializer(messages, many=True, context={'request': request})
    
    return Response(serializer.data, status=status.HTTP_200_OK)

# --- NEU: Liste aller Konversationen eines Benutzers ---
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_user_conversations(request):
    """
    Gibt eine Liste aller Konversationen zurück, an denen der aktuelle Benutzer beteiligt ist.
    Jede Konversation enthält Informationen über den anderen Benutzer und die letzte Nachricht.
    
    Query-Parameter:
    - unread: Wenn 'true', werden nur unbeantwortete Konversationen zurückgegeben
    """
    user = request.user
    unread_filter = request.query_params.get('unread', 'false').lower() == 'true'
    
    # Alle Nachrichten finden, an denen der Benutzer beteiligt ist
    user_messages = Message.objects.filter(
        Q(sender=user) | Q(recipient=user)
    ).select_related('sender', 'recipient')
    
    # Für jeden Gesprächspartner die neueste Nachricht finden
    conversation_partners = set()
    for message in user_messages:
        other_user = message.recipient if message.sender == user else message.sender
        conversation_partners.add(other_user.id)
    
    conversations = []
    for partner_id in conversation_partners:
        try:
            partner = CustomUser.objects.get(pk=partner_id)
            
            # Neueste Nachricht in dieser Konversation finden
            latest_message = Message.objects.filter(
                (Q(sender=user) & Q(recipient=partner)) | 
                (Q(sender=partner) & Q(recipient=user))
            ).order_by('-timestamp').first()
            
            # Prüfen, ob die letzte Nachricht vom Partner ist und unbeantwortet
            is_unanswered = False
            if latest_message and latest_message.sender == partner:
                # Prüfen, ob es eine neuere Nachricht vom Benutzer gibt
                user_reply = Message.objects.filter(
                    sender=user, 
                    recipient=partner,
                    timestamp__gt=latest_message.timestamp
                ).exists()
                is_unanswered = not user_reply
            
            # Wenn unread=true, nur unbeantwortete Konversationen hinzufügen
            if unread_filter and not is_unanswered:
                continue
            
            if latest_message:
                # Verwende PublicUserSerializer für die Benutzerinformationen
                from accounts.serializers import PublicUserSerializer
                partner_serializer = PublicUserSerializer(partner, context={'request': request})
                
                conversations.append({
                    'other_user': {
                        'id': partner.id,
                        'username': partner.username,
                        'profile_picture_url': partner_serializer.get_profile_picture_url(partner)
                    },
                    'last_message': {
                        'id': latest_message.id,
                        'content': latest_message.content[:100] + ('...' if len(latest_message.content) > 100 else ''),
                        'timestamp': latest_message.timestamp,
                        'is_from_user': latest_message.sender == user
                    },
                    'is_unanswered': is_unanswered
                })
        except CustomUser.DoesNotExist:
            continue
    
    # Sortieren nach Zeitstempel der letzten Nachricht (neueste zuerst)
    conversations.sort(key=lambda x: x['last_message']['timestamp'], reverse=True)
    
    return Response(conversations, status=status.HTTP_200_OK)

# --- list_moderator_conversations ---
@api_view(['GET'])
@permission_classes([IsAdminUser])
def list_moderator_conversations(request):
    requesting_user = request.user
    unanswered_filter = request.query_params.get('unanswered', 'false').lower() == 'true'
    # Get all conversations between real users (senders) and fake users (recipients)
    base_query = Message.objects.filter(sender__is_fake=False, recipient__is_fake=True)
    
    # Filter by assigned moderator if not superuser
    if not requesting_user.is_superuser: 
        base_query = base_query.filter(recipient__assigned_moderator=requesting_user)
    
    # Get unique sender-recipient pairs
    conversation_pairs = base_query.values('sender', 'recipient').distinct()
    
    # For each pair, get the latest message
    latest_message_ids = []
    for pair in conversation_pairs:
        latest_message = Message.objects.filter(
            sender_id=pair['sender'], 
            recipient_id=pair['recipient']
        ).order_by('-timestamp').first()
        
        if latest_message:
            latest_message_ids.append(latest_message.id)
    
    # Get all the latest messages
    latest_messages = Message.objects.filter(id__in=latest_message_ids).select_related('sender', 'recipient').order_by('-timestamp')
    conversation_summaries = []
    if unanswered_filter:
        for m in latest_messages:
            real_user = m.sender
            fake_user = m.recipient
            try: # <-- TRY Ebene 2
                actual_last_message = Message.objects.filter(
                    (Q(sender=real_user, recipient=fake_user) | Q(sender=fake_user, recipient=real_user))
                ).latest('timestamp') # Ebene 3
                if actual_last_message.sender_id == real_user.id: # Ebene 3
                    conversation_summaries.append({ # Ebene 4
                        'real_user': real_user,
                        'fake_user': fake_user,
                        'last_message_content': actual_last_message.content[:100] + ('...' if len(actual_last_message.content) > 100 else ''),
                        'last_message_timestamp': actual_last_message.timestamp
                    }) # Ende Ebene 4
            except Message.DoesNotExist: # <-- EXCEPT Ebene 2 (gleich wie try)
                continue # Ebene 3
    else:
        for m in latest_messages:
            conversation_summaries.append({
                'real_user': m.sender, 'fake_user': m.recipient,
                'last_message_content': m.content[:100] + ('...' if len(m.content) > 100 else ''),
                'last_message_timestamp': m.timestamp
            })
    serializer = ModeratorConversationSerializer(conversation_summaries, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

# --- get_moderator_conversation_view ---
@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_moderator_conversation_view(request, real_user_id, fake_user_id):
    requesting_user = request.user
    try: # <-- TRY Ebene 1
        real_user = CustomUser.objects.get(pk=real_user_id, is_fake=False) # Ebene 2
        fake_user = CustomUser.objects.get(pk=fake_user_id, is_fake=True) # Ebene 2
    except (CustomUser.DoesNotExist, ValueError, TypeError): # <-- EXCEPT Ebene 1
        return Response({"detail": "One or both user IDs invalid or users not found/type mismatch."}, status=status.HTTP_404_NOT_FOUND) # Ebene 2

    if not requesting_user.is_superuser: # Ebene 1
        if fake_user.assigned_moderator_id != requesting_user.id: # Ebene 2
            return Response({"detail": "You are not assigned to this fake user's conversations."}, status=status.HTTP_403_FORBIDDEN) # Ebene 3

    messages = Message.objects.filter( # Ebene 1
        (Q(sender=real_user) & Q(recipient=fake_user)) |
        (Q(sender=fake_user) & Q(recipient=real_user))
    ).select_related('sender', 'recipient').order_by('timestamp')
    serializer = MessageSerializer(messages, many=True) # Ebene 1
    return Response(serializer.data, status=status.HTTP_200_OK) # Ebene 1

# --- moderator_reply_view ---
@api_view(['POST'])
@permission_classes([IsAdminUser])
def moderator_reply_view(request):
    requesting_user = request.user; fake_user_id = request.data.get('fake_user_id'); real_user_id = request.data.get('real_user_id'); content = request.data.get('content')
    if not fake_user_id or not real_user_id or not content: return Response({"error": "Missing required fields (fake_user_id, real_user_id, content)."}, status=status.HTTP_400_BAD_REQUEST)
    if not content.strip(): return Response({"error": "Message content cannot be empty."}, status=status.HTTP_400_BAD_REQUEST)
    try: fake_user = CustomUser.objects.get(pk=fake_user_id, is_fake=True); real_user = CustomUser.objects.get(pk=real_user_id, is_fake=False)
    except (CustomUser.DoesNotExist, ValueError, TypeError): return Response({"error": "Invalid user ID(s) or type mismatch."}, status=status.HTTP_404_NOT_FOUND)
    if not requesting_user.is_superuser:
        if fake_user.assigned_moderator_id != requesting_user.id: return Response({"detail": "You are not assigned to reply as this fake user."}, status=status.HTTP_403_FORBIDDEN)
    try: 
        # Nachricht erstellen
        message = Message.objects.create(sender=fake_user, recipient=real_user, content=content)
        
        # Benachrichtigung für den echten Benutzer erstellen
        from notifications.models import Notification, NotificationType
        Notification.objects.create(
            user=real_user,
            type=NotificationType.MESSAGE,
            sender=fake_user,
            content=f"{fake_user.username} hat dir eine neue Nachricht gesendet.",
            reference_id=message.id,
            reference_model='Message'
        )
        
        serializer = MessageSerializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Exception as e: print(f"ERROR: Could not create message in moderator_reply_view: {e}"); return Response({"error": "Could not save message due to a server error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# --- AI Suggestion View ---
class AISuggestionView(APIView):
    permission_classes = [IsAdminUser]
    def post(self, request, *args, **kwargs):
        requesting_user = request.user
        real_user_id = request.data.get('real_user_id'); fake_user_id = request.data.get('fake_user_id')
        if not real_user_id or not fake_user_id: return Response({"detail": "real_user_id and fake_user_id are required."}, status=status.HTTP_400_BAD_REQUEST)
        try: real_user_id = int(real_user_id); fake_user_id = int(fake_user_id)
        except (ValueError, TypeError): return Response({"detail": "Invalid user ID format."}, status=status.HTTP_400_BAD_REQUEST)

        try: # <-- TRY für User Ebene 2
            real_user = CustomUser.objects.get(pk=real_user_id, is_fake=False) # Ebene 3
            fake_user = CustomUser.objects.get(pk=fake_user_id, is_fake=True) # Ebene 3
        except CustomUser.DoesNotExist: # <-- EXCEPT Ebene 2
            return Response({"detail": "Real or Fake User not found."}, status=status.HTTP_404_NOT_FOUND) # Ebene 3

        try: # <-- TRY für Settings Ebene 2
            conv_settings = ConversationAiSettings.objects.get(real_user=real_user, fake_user=fake_user) # Ebene 3
            if conv_settings.ai_mode != ConversationAiSettings.AiMode.ASSISTED: # Ebene 3
                return Response({"detail": "AI assistance is not enabled for this conversation."}, status=status.HTTP_403_FORBIDDEN) # Ebene 4
        except ConversationAiSettings.DoesNotExist: # <-- EXCEPT Ebene 2 (korrekt unter try)
            return Response({"detail": "AI settings not found for this conversation (default is NONE)."}, status=status.HTTP_403_FORBIDDEN) # Ebene 3

        if not requesting_user.can_use_ai_assist: # Ebene 2
             raise PermissionDenied("You do not have permission to use the AI assist feature.") # Ebene 3

        messages = Message.objects.filter( (Q(sender=real_user, recipient=fake_user) | Q(sender=fake_user, recipient=real_user)) ).select_related('sender').order_by('-timestamp')[:CONVERSATION_HISTORY_LENGTH] # Ebene 2
        messages_history = reversed(list(messages)); ai_prompt = fake_user.ai_personality_prompt # Ebene 2
        if not ai_prompt: ai_prompt = f"You are {fake_user.username}, a friendly person on a dating platform." # Ebene 2
        openai_messages = [{"role": "system", "content": ai_prompt}] # Ebene 2
        for msg in messages_history: # Ebene 2
            if msg.sender == fake_user: openai_messages.append({"role": "assistant", "content": msg.content}) # Ebene 3
            else: openai_messages.append({"role": "user", "content": msg.content}) # Ebene 3

        api_key = settings.OPENAI_API_KEY # Ebene 2
        if not api_key: print("ERROR: OPENAI_API_KEY not configured..."); return Response({"detail": "AI service not configured."}, status=status.HTTP_503_SERVICE_UNAVAILABLE) # Ebene 2

        try: # <-- TRY für OpenAI Ebene 2
            client = openai.OpenAI(api_key=api_key) # Ebene 3
            completion = client.chat.completions.create( model="gpt-3.5-turbo", messages=openai_messages) # Ebene 3
            suggestion = completion.choices[0].message.content.strip() # Ebene 3
            if not suggestion: return Response({"detail": "AI returned an empty suggestion."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) # Ebene 3
            return Response({"suggestion": suggestion}, status=status.HTTP_200_OK) # Ebene 3
        except openai.AuthenticationError: print("ERROR: OpenAI Authentication failed..."); return Response({"detail": "AI service authentication error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) # Ebene 2
        except openai.RateLimitError: print("ERROR: OpenAI Rate Limit exceeded."); return Response({"detail": "AI service rate limit exceeded."}, status=status.HTTP_429_TOO_MANY_REQUESTS) # Ebene 2
        except openai.APIError as e: print(f"ERROR: OpenAI API Error: {e}"); return Response({"detail": f"AI service unavailable or error: {e}"}, status=status.HTTP_503_SERVICE_UNAVAILABLE) # Ebene 2
        except Exception as e: print(f"ERROR: Unexpected error calling OpenAI: {e}"); return Response({"detail": "An unexpected error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) # Ebene 2

# --- Erweiterte AI Suggestion View ---
class EnhancedAISuggestionView(APIView):
    """
    Erweiterte Version der AI-Suggestion-View, die mehrere Antwortvorschläge
    mit unterschiedlichen Kommunikationsstilen generiert.
    """
    permission_classes = [IsAdminUser]
    
    # Standard-Kommunikationsstile, falls keine spezifischen angegeben werden
    DEFAULT_STYLES = [
        {
            "name": "friendly",
            "description": "Freundlich und unverbindlich",
            "instruction": "Antworte in einem freundlichen, leichten und unverbindlichen Ton."
        },
        {
            "name": "deep",
            "description": "Tiefergehend und persönlich",
            "instruction": "Antworte in einem tiefgründigen, nachdenklichen und persönlichen Ton. Teile Gedanken und Gefühle."
        },
        {
            "name": "flirty",
            "description": "Flirty und spielerisch",
            "instruction": "Antworte in einem flirtenden, spielerischen und leicht neckischen Ton. Verwende Emojis und sei charmant."
        },
        {
            "name": "questioning",
            "description": "Fragend und interessiert",
            "instruction": "Antworte mit Interesse und stelle Fragen, um mehr über die andere Person zu erfahren."
        }
    ]
    
    def post(self, request, *args, **kwargs):
        requesting_user = request.user
        real_user_id = request.data.get('real_user_id')
        fake_user_id = request.data.get('fake_user_id')
        num_suggestions = int(request.data.get('num_suggestions', 4))  # Standardmäßig 4 Vorschläge
        custom_styles = request.data.get('styles', None)  # Optionale benutzerdefinierte Stile
        
        # Validierung der Eingabeparameter
        if not real_user_id or not fake_user_id:
            return Response({"detail": "real_user_id and fake_user_id are required."}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        try:
            real_user_id = int(real_user_id)
            fake_user_id = int(fake_user_id)
        except (ValueError, TypeError):
            return Response({"detail": "Invalid user ID format."}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        # Begrenzung der Anzahl der Vorschläge
        if num_suggestions < 1 or num_suggestions > 5:
            return Response({"detail": "num_suggestions must be between 1 and 5."}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        # Benutzer abrufen
        try:
            real_user = CustomUser.objects.get(pk=real_user_id, is_fake=False)
            fake_user = CustomUser.objects.get(pk=fake_user_id, is_fake=True)
        except CustomUser.DoesNotExist:
            return Response({"detail": "Real or Fake User not found."}, 
                           status=status.HTTP_404_NOT_FOUND)
        
        # Überprüfen der AI-Einstellungen
        try:
            conv_settings = ConversationAiSettings.objects.get(real_user=real_user, fake_user=fake_user)
            if conv_settings.ai_mode != ConversationAiSettings.AiMode.ASSISTED:
                return Response({"detail": "AI assistance is not enabled for this conversation."}, 
                               status=status.HTTP_403_FORBIDDEN)
        except ConversationAiSettings.DoesNotExist:
            return Response({"detail": "AI settings not found for this conversation (default is NONE)."}, 
                           status=status.HTTP_403_FORBIDDEN)
        
        # Überprüfen der Berechtigungen
        if not requesting_user.can_use_ai_assist:
            raise PermissionDenied("You do not have permission to use the AI assist feature.")
        
        # Nachrichten für den Kontext abrufen
        messages = Message.objects.filter(
            (Q(sender=real_user, recipient=fake_user) | Q(sender=fake_user, recipient=real_user))
        ).select_related('sender').order_by('-timestamp')[:CONVERSATION_HISTORY_LENGTH]
        
        messages_history = reversed(list(messages))
        
        # Basis-Prompt für die Persönlichkeit des Fake-Users
        ai_prompt = fake_user.ai_personality_prompt
        if not ai_prompt:
            ai_prompt = f"You are {fake_user.username}, a friendly person on a dating platform."
        
        # Stile für die Antworten festlegen
        styles_to_use = custom_styles if custom_styles else self.DEFAULT_STYLES[:num_suggestions]
        
        # Ergebnisse vorbereiten
        suggestions = []
        
        # API-Key überprüfen
        api_key = settings.OPENAI_API_KEY
        if not api_key:
            print("ERROR: OPENAI_API_KEY not configured...")
            return Response({"detail": "AI service not configured."}, 
                           status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        try:
            client = openai.OpenAI(api_key=api_key)
            
            # Für jeden Stil einen Vorschlag generieren
            for style in styles_to_use[:num_suggestions]:
                # Basis-Prompt mit dem spezifischen Stil kombinieren
                style_prompt = f"{ai_prompt} {style['instruction']}"
                
                # Nachrichten für die API vorbereiten
                openai_messages = [{"role": "system", "content": style_prompt}]
                
                for msg in messages_history:
                    if msg.sender == fake_user:
                        openai_messages.append({"role": "assistant", "content": msg.content})
                    else:
                        openai_messages.append({"role": "user", "content": msg.content})
                
                # API-Anfrage senden
                completion = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=openai_messages
                )
                
                suggestion_content = completion.choices[0].message.content.strip()
                
                if suggestion_content:
                    suggestions.append({
                        "name": style["name"],
                        "description": style["description"],
                        "content": suggestion_content
                    })
            
            if not suggestions:
                return Response({"detail": "AI returned empty suggestions."}, 
                               status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            return Response({"suggestions": suggestions}, status=status.HTTP_200_OK)
            
        except openai.AuthenticationError:
            print("ERROR: OpenAI Authentication failed...")
            return Response({"detail": "AI service authentication error."}, 
                           status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except openai.RateLimitError:
            print("ERROR: OpenAI Rate Limit exceeded.")
            return Response({"detail": "AI service rate limit exceeded."}, 
                           status=status.HTTP_429_TOO_MANY_REQUESTS)
        except openai.APIError as e:
            print(f"ERROR: OpenAI API Error: {e}")
            return Response({"detail": f"AI service unavailable or error: {e}"}, 
                           status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as e:
            print(f"ERROR: Unexpected error calling OpenAI: {e}")
            return Response({"detail": "An unexpected error occurred."}, 
                           status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# --- Conversation AI Settings View ---
class ConversationAiSettingsDetailView(APIView):
    permission_classes = [IsAdminUser]
    
    def get(self, request, real_user_id, fake_user_id, *args, **kwargs):
        try:
            real_user = CustomUser.objects.get(pk=real_user_id, is_fake=False)
            fake_user = CustomUser.objects.get(pk=fake_user_id, is_fake=True)
        except CustomUser.DoesNotExist:
            return Response({"detail": "One or both users not found."}, status=status.HTTP_404_NOT_FOUND)
        
        settings, created = ConversationAiSettings.objects.get_or_create(
            real_user=real_user,
            fake_user=fake_user,
            defaults={'ai_mode': ConversationAiSettings.AiMode.NONE}
        )
        
        serializer = ConversationAiSettingsSerializer(settings)
        return Response(serializer.data)
    
    def patch(self, request, real_user_id, fake_user_id, *args, **kwargs):
        try:
            real_user = CustomUser.objects.get(pk=real_user_id, is_fake=False)
            fake_user = CustomUser.objects.get(pk=fake_user_id, is_fake=True)
        except CustomUser.DoesNotExist:
            return Response({"detail": "One or both users not found."}, status=status.HTTP_404_NOT_FOUND)
        
        settings, created = ConversationAiSettings.objects.get_or_create(
            real_user=real_user,
            fake_user=fake_user,
            defaults={'ai_mode': ConversationAiSettings.AiMode.NONE}
        )
        
        serializer = ConversationAiSettingsSerializer(settings, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# --- Nachrichtenanhänge ---
class MessageAttachmentUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        message_id = request.data.get('message_id')
        file = request.data.get('file')
        
        if not message_id or not file:
            return Response({"detail": "message_id and file are required."}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        try:
            message = Message.objects.get(pk=message_id)
        except Message.DoesNotExist:
            return Response({"detail": "Message not found."}, 
                           status=status.HTTP_404_NOT_FOUND)
        
        # Überprüfen, ob der Benutzer der Absender der Nachricht ist
        if message.sender != request.user:
            return Response({"detail": "You can only attach files to your own messages."}, 
                           status=status.HTTP_403_FORBIDDEN)
        
        # Anhang erstellen
        attachment = MessageAttachment.objects.create(
            message=message,
            file=file
        )
        
        serializer = MessageAttachmentSerializer(attachment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# --- Konversation mit Anhängen ---
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_conversation_with_attachments_view(request, other_user_id):
    user = request.user
    
    try:
        other_user = CustomUser.objects.get(pk=other_user_id)
    except CustomUser.DoesNotExist:
        return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
    
    if user.id == other_user_id:
        return Response({"detail": "Cannot retrieve conversation with yourself."}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    messages = Message.objects.filter(
        (Q(sender=user) & Q(recipient=other_user)) | 
        (Q(sender=other_user) & Q(recipient=user))
    ).select_related('sender', 'recipient').prefetch_related('attachments').order_by('timestamp')
    
    # Verwende PublicMessageWithAttachmentsSerializer für echte Benutzer, MessageWithAttachmentsSerializer für Moderatoren
    if user.is_staff:
        serializer = MessageWithAttachmentsSerializer(messages, many=True, context={'request': request})
    else:
        serializer = PublicMessageWithAttachmentsSerializer(messages, many=True, context={'request': request})
    
    return Response(serializer.data)

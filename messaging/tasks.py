# messaging/tasks.py (Mit implementierter AI Auto-Reply Logik)

from background_task import background
from django.conf import settings
from django.db.models import Q
from django.shortcuts import get_object_or_404 # Besser für User-Fetching
import openai
import time # Optional für zusätzliches Logging/Debugging
import random # Für die zufällige Verzögerung später im Signal

# Importiere Modelle sicher innerhalb der Task-Funktion
# um Probleme mit der App-Registry beim Start zu vermeiden.

# Konstante für Chat-Historie
CONVERSATION_HISTORY_LENGTH = 15

# Der Decorator @background macht die Funktion zu einem Task.
# schedule=0 ist der Default, die tatsächliche Verzögerung
# wird beim Aufruf im Signal Handler gesetzt.
@background(schedule=0)
def generate_and_send_ai_reply(real_user_id, fake_user_id):
    """
    Background task to generate a reply using OpenAI and send it as the fake user.
    Triggered (usually with a delay) by a signal.
    """
    # Importiere Modelle hier drin
    from .models import Message, ConversationAiSettings
    from accounts.models import CustomUser
    print(f"TASK STARTED: generate_and_send_ai_reply for real_user_id={real_user_id}, fake_user_id={fake_user_id}")
    start_time = time.time()

    try:
        # 1. User-Objekte holen
        # Wir verwenden get_object_or_404 hier nicht direkt,
        # da wir den Fehler spezifischer loggen wollen.
        try:
            real_user = CustomUser.objects.get(pk=real_user_id, is_fake=False)
            fake_user = CustomUser.objects.get(pk=fake_user_id, is_fake=True)
        except CustomUser.DoesNotExist:
            print(f"TASK FAILED [User Fetch]: User not found for real_user_id={real_user_id} or fake_user_id={fake_user_id}")
            return # Beende den Task hier

        # 2. Prüfen, ob Modus wirklich noch AUTO ist (optionaler Sicherheitscheck)
        # Könnte sich geändert haben, seit der Task geplant wurde.
        try:
            settings_mode = ConversationAiSettings.objects.get(real_user=real_user, fake_user=fake_user).ai_mode
            if settings_mode != ConversationAiSettings.AiMode.AUTO:
                print(f"TASK SKIPPED: AI mode for {real_user_id}<->{fake_user_id} is no longer AUTO (now {settings_mode}).")
                return # Beende den Task, da nicht mehr AUTO
        except ConversationAiSettings.DoesNotExist:
             print(f"TASK SKIPPED: AI settings for {real_user_id}<->{fake_user_id} not found (implies NONE).")
             return # Beende den Task

        # 3. Konversationshistorie holen (letzte N Nachrichten)
        messages = Message.objects.filter(
            (Q(sender=real_user, recipient=fake_user) |
             Q(sender=fake_user, recipient=real_user))
        ).select_related('sender').order_by('-timestamp')[:CONVERSATION_HISTORY_LENGTH]
        messages_history = reversed(list(messages))

        # 4. AI Personality Prompt vom Fake User holen
        ai_prompt = fake_user.ai_personality_prompt
        if not ai_prompt or not ai_prompt.strip():
            ai_prompt = f"You are {fake_user.username}, a friendly person on a dating platform." # Minimaler Default-Prompt
            print(f"WARNUNG: Using default AI prompt for fake_user_id={fake_user_id}")

        # 5. Prompt für OpenAI formatieren
        openai_messages = [{"role": "system", "content": ai_prompt}]
        for msg in messages_history:
            role = "assistant" if msg.sender_id == fake_user.id else "user"
            openai_messages.append({"role": role, "content": msg.content})

        # 6. OpenAI API aufrufen
        api_key = settings.OPENAI_API_KEY
        if not api_key:
            print(f"TASK FAILED [Config]: OPENAI_API_KEY not configured.")
            return # Beende den Task

        # 7. Antwort von OpenAI holen und 8. Neue Nachricht speichern
        try:
            client = openai.OpenAI(api_key=api_key)
            print(f"TASK INFO: Calling OpenAI for {real_user_id}<->{fake_user_id}...")
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo", # Oder anderes Modell
                messages=openai_messages
            )
            suggestion = completion.choices[0].message.content.strip()

            if suggestion:
                print(f"TASK INFO: OpenAI suggestion received for {real_user_id}<->{fake_user_id}. Saving message...")
                # Erstelle und speichere die Antwort-Nachricht
                Message.objects.create(
                    sender=fake_user,
                    recipient=real_user,
                    content=suggestion
                )
                print(f"TASK SUCCESS: AI Reply sent for {real_user_id}<->{fake_user_id}.")
            else:
                print(f"TASK WARN: OpenAI returned an empty suggestion for {real_user_id}<->{fake_user_id}.")

        # Fehlerbehandlung für OpenAI
        except openai.AuthenticationError:
             print(f"TASK FAILED [OpenAI Auth]: OpenAI Authentication failed for {real_user_id}<->{fake_user_id}. Check API Key.")
        except openai.RateLimitError:
             print(f"TASK FAILED [OpenAI RateLimit]: OpenAI Rate Limit exceeded for {real_user_id}<->{fake_user_id}.")
             # Hier könnte man den Task für später neu planen (django-background-tasks kann das)
        except openai.APIError as e:
            print(f"TASK FAILED [OpenAI API]: OpenAI API Error for {real_user_id}<->{fake_user_id}: {e}")
        except Exception as e:
            print(f"TASK FAILED [OpenAI Unexpected]: Unexpected error calling OpenAI for {real_user_id}<->{fake_user_id}: {e}")

    except Exception as e:
        # Fange alle anderen unerwarteten Fehler im Task ab
        print(f"TASK FAILED [General]: Unexpected error in generate_and_send_ai_reply for {real_user_id}<->{fake_user_id}: {e}")
        # Optional: Fehler erneut werfen, wenn django-background-tasks ihn loggen soll
        # raise e
    finally:
        end_time = time.time()
        print(f"TASK FINISHED: generate_and_send_ai_reply for {real_user_id}<->{fake_user_id} took {end_time - start_time:.2f} seconds.")


# Ende der Datei messaging/tasks.py
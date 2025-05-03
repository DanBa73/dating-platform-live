# messaging/signals.py (Liest Delay aus Settings)

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings # Import von settings ist schon da
import random

# Modelle und Task werden innerhalb der Funktion importiert für Sicherheit

@receiver(post_save, sender='messaging.Message')
def trigger_ai_auto_reply(sender, instance, created, **kwargs):
    """
    Signal handler called after a Message instance is saved.
    Checks if the message should trigger an AI auto-reply task.
    """
    from .tasks import generate_and_send_ai_reply
    from .models import ConversationAiSettings, Message
    from accounts.models import CustomUser

    print(f"SIGNAL trigger_ai_auto_reply: Called for Message ID {instance.id}, created={created}")

    if created:
        message_instance = instance
        sender_is_real = not message_instance.sender.is_fake
        recipient_is_fake = message_instance.recipient.is_fake

        if sender_is_real and recipient_is_fake:
            print(f"SIGNAL: Message from Real User {message_instance.sender_id} to Fake User {message_instance.recipient_id}. Checking AI mode...")
            real_user = message_instance.sender
            fake_user = message_instance.recipient

            setting = ConversationAiSettings.objects.filter(
                real_user=real_user, fake_user=fake_user
            ).first()

            if setting and setting.ai_mode == ConversationAiSettings.AiMode.AUTO:
                print(f"SIGNAL: AI Mode is AUTO for {real_user.id}<->{fake_user.id}. Scheduling task...")

                # --- GEÄNDERT: Werte aus settings.py lesen ---
                min_delay = settings.AI_AUTO_REPLY_MIN_DELAY_SECONDS
                max_delay = settings.AI_AUTO_REPLY_MAX_DELAY_SECONDS

                # Sicherheitscheck: Falls min > max, verwende min als max.
                if min_delay > max_delay:
                    print(f"WARNUNG: AI_AUTO_REPLY_MIN_DELAY ({min_delay}) > MAX_DELAY ({max_delay}). Using min_delay as max_delay.")
                    max_delay = min_delay
                # --- ENDE ÄNDERUNG ---

                delay_seconds = random.randint(min_delay, max_delay)
                print(f"SIGNAL: Calculated random delay: {delay_seconds} seconds (using settings).")

                generate_and_send_ai_reply(
                    real_user.id,
                    fake_user.id,
                    schedule=delay_seconds
                )
                print(f"SIGNAL: Task generate_and_send_ai_reply scheduled for {real_user.id}<->{fake_user.id} in {delay_seconds} seconds.")

            else:
                mode = setting.ai_mode if setting else 'NONE (no setting found)'
                print(f"SIGNAL: AI Mode is '{mode}' for {real_user.id}<->{fake_user.id}. No AUTO task scheduled.")
        else:
             print(f"SIGNAL: Message not from Real to Fake User. Skipping AI trigger.")
    else:
        print(f"SIGNAL: Message ID {instance.id} was updated, not created. Skipping AI trigger.")

# Ende der Datei messaging/signals.py
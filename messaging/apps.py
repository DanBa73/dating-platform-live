# messaging/apps.py (Mit Signal-Import in ready())

from django.apps import AppConfig

class MessagingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'messaging'

    # --- NEU: ready Methode zum Importieren der Signale ---
    def ready(self):
        """
        Diese Methode wird aufgerufen, wenn Django die App lädt.
        Wir importieren hier die Signale, damit die Receiver verbunden werden.
        """
        try:
            import messaging.signals # Importiert unsere signals.py Datei
            print("Messaging signals imported successfully.") # Optional: Bestätigung im Log
        except ImportError:
            pass # Ignoriere Fehler, falls signals.py (noch) nicht existiert
    # --- ENDE NEU ---

# Ende der Datei messaging/apps.py
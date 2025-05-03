from django.db import models
from accounts.models import CustomUser

class NotificationType(models.TextChoices):
    LIKE = 'like', 'Neuer Like'
    MESSAGE = 'message', 'Neue Nachricht'
    SYSTEM = 'system', 'Systemnachricht'

class Notification(models.Model):
    """
    Modell für Benutzerbenachrichtigungen wie Likes, Nachrichten usw.
    """
    user = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='notifications',
        help_text="Benutzer, der die Benachrichtigung erhält"
    )
    type = models.CharField(
        max_length=20, 
        choices=NotificationType.choices,
        help_text="Art der Benachrichtigung"
    )
    sender = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='sent_notifications',
        help_text="Benutzer, der die Aktion ausgelöst hat (falls zutreffend)"
    )
    content = models.TextField(
        help_text="Inhalt der Benachrichtigung"
    )
    is_read = models.BooleanField(
        default=False,
        help_text="Gibt an, ob die Benachrichtigung gelesen wurde"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Zeitpunkt der Erstellung der Benachrichtigung"
    )
    reference_id = models.IntegerField(
        null=True, 
        blank=True,
        help_text="ID des referenzierten Objekts (z.B. Like-ID, Nachrichten-ID)"
    )
    reference_model = models.CharField(
        max_length=50, 
        null=True, 
        blank=True,
        help_text="Name des referenzierten Modells (z.B. 'Like', 'Message')"
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Benachrichtigung"
        verbose_name_plural = "Benachrichtigungen"
    
    def __str__(self):
        return f"{self.get_type_display()} für {self.user.username}"

class PushSubscription(models.Model):
    """
    Modell für Push-Benachrichtigungsabonnements
    """
    user = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='push_subscriptions',
        help_text="Benutzer, dem dieses Push-Abonnement gehört"
    )
    subscription_info = models.TextField(
        help_text="JSON-String mit den Abonnementinformationen"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Zeitpunkt der Erstellung des Abonnements"
    )
    last_used = models.DateTimeField(
        auto_now=True,
        help_text="Zeitpunkt der letzten Verwendung des Abonnements"
    )
    
    class Meta:
        verbose_name = "Push-Abonnement"
        verbose_name_plural = "Push-Abonnements"
    
    def __str__(self):
        return f"Push-Abonnement für {self.user.username}"

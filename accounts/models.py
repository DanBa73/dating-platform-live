# accounts/models.py (Mit about_me, gender, seeking Feldern) # <- Name im Kommentar angepasst
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

# --- NEU: Choices für Geschlecht ---
class GenderChoices(models.TextChoices):
    MALE = 'MALE', _('Male')
    FEMALE = 'FEMALE', _('Female')
    # Optional: Weitere Choices hinzufügen, falls benötigt (z.B. OTHER, UNKNOWN)
# --- ENDE NEU ---

class CustomUser(AbstractUser):
    # Bestehende Felder...
    is_fake = models.BooleanField(default=False, help_text=_('Designates whether this user is a fake profile managed internally.'))
    ai_personality_prompt = models.TextField(blank=True, null=True, help_text=_('Personality prompt for AI interactions (only used for fake users).'))
    coin_balance = models.IntegerField(default=25, help_text=_("User's current coin balance."))
    assigned_moderator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name='managed_fake_profiles',
        limit_choices_to={'is_staff': True},
        help_text=_("Moderator assigned to manage this fake profile (only relevant if is_fake=True).")
    )
    moderator_notes = models.TextField(
        blank=True, null=True,
        help_text=_("Internal notes for moderators about this user (especially if real user).")
    )
    can_use_ai_assist = models.BooleanField(
        default=False,
        help_text=_('Can this staff user use the AI assist feature (Mode 2)? Only relevant if is_staff=True.')
    )

    # --- Felder für User-Profil ---
    birth_date = models.DateField(null=True, blank=True, verbose_name=_('Birth Date'))
    postal_code = models.CharField(max_length=20, null=True, blank=True, verbose_name=_('Postal Code'))
    city = models.CharField(max_length=100, null=True, blank=True, verbose_name=_('City'))
    state = models.CharField(max_length=100, null=True, blank=True, verbose_name=_('State/Province'))
    country = models.CharField(max_length=100, null=True, blank=True, verbose_name=_('Country'))
    about_me = models.TextField(
        blank=True, null=True, verbose_name=_('About Me'), help_text=_('A short description about the user.')
    )
    # --- Korrektur: Gender / Seeking Felder --- # <- Kommentar angepasst
    gender = models.CharField(
        max_length=10, # Ausreichend für 'MALE'/'FEMALE' etc.
        choices=GenderChoices.choices,
        null=True, # Erlaubt NULL in der DB
        blank=True, # Erlaubt leeres Feld im Formular
        verbose_name=_('Gender')
    )
    # --- HIER WURDE DER NAME GEÄNDERT ---
    seeking = models.CharField( # <<< Umbenannt von seeking_gender
        max_length=10,
        choices=GenderChoices.choices,
        null=True,
        blank=True,
        verbose_name=_('Seeking Gender') # Beschreibung kann bleiben
    )
    # --- ENDE KORREKTUR ---
    # --- ENDE Profilfelder ---


    # M2M Felder (unverändert)
    groups = models.ManyToManyField(
        'auth.Group', verbose_name=_('groups'), blank=True,
        help_text=_('The groups this user belongs to...'),
        related_name="customuser_set", related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission', verbose_name=_('user permissions'), blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name="customuser_set", related_query_name="user",
    )

    def __str__(self):
        return self.username

# --- UserProfileImage Model (unverändert) ---
class UserProfileImage(models.Model):
    user = models.ForeignKey( settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile_images' )
    image = models.ImageField( upload_to='profile_pics/', )
    is_approved = models.BooleanField( default=False, help_text=_("Is this image approved by admin/moderator?") )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.user.username} (ID: {self.id}, Approved: {self.is_approved})"

    class Meta:
        ordering = ['uploaded_at']

# --- NEU: Like Model ---
class Like(models.Model):
    """
    Speichert Likes zwischen Benutzern.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='likes_given',
        help_text=_("Benutzer, der den Like gegeben hat")
    )
    liked_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='likes_received',
        help_text=_("Benutzer, der den Like erhalten hat")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Like')
        verbose_name_plural = _('Likes')
        # Stellt sicher, dass ein Benutzer einen anderen nur einmal liken kann
        constraints = [
            models.UniqueConstraint(fields=['user', 'liked_user'], name='unique_like')
        ]
        ordering = ['-created_at']  # Neueste Likes zuerst
    
    def __str__(self):
        return f"{self.user.username} likes {self.liked_user.username}"
# --- ENDE NEU ---

# Ende der Datei accounts/models.py

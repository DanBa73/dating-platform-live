# accounts/admin.py (Mit Massenlike-Funktion)
from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponseRedirect
from django.urls import path
from django.shortcuts import render
from django import forms
from django.db import transaction

from .models import CustomUser, UserProfileImage, Like
from messaging.models import Message

# --- Formular für Massenlike-Funktion ---
class MassLikeForm(forms.Form):
    fake_user = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(is_fake=True),
        label="Fake-Profil auswählen",
        help_text="Wählen Sie das Fake-Profil, das die Likes senden soll."
    )
    postal_code_prefix = forms.CharField(
        max_length=5, 
        required=False,
        label="Postleitzahl-Präfix",
        help_text="Nur Benutzer liken, deren Postleitzahl mit diesem Präfix beginnt (z.B. '8' für alle PLZ, die mit 8 beginnen)."
    )
    state = forms.CharField(
        max_length=100, 
        required=False,
        label="Bundesland",
        help_text="Nur Benutzer liken, die in diesem Bundesland wohnen."
    )

# --- Gemeinsame Massenlike-Funktion ---
def mass_like_view(self, request, model_admin):
    if request.method == 'POST':
        form = MassLikeForm(request.POST)
        if form.is_valid():
            fake_user = form.cleaned_data['fake_user']
            postal_code_prefix = form.cleaned_data['postal_code_prefix']
            state = form.cleaned_data['state']
            
            # Benutzer filtern basierend auf den Kriterien
            users_query = CustomUser.objects.filter(is_active=True)
            
            # Anwenden der Filter
            if postal_code_prefix:
                users_query = users_query.filter(postal_code__startswith=postal_code_prefix)
            
            if state:
                users_query = users_query.filter(state__iexact=state)
            
            # Wichtig: Das Fake-Profil selbst ausschließen
            users_query = users_query.exclude(pk=fake_user.pk)
            
            # Nur echte Benutzer liken (keine Fake-Profile)
            users_query = users_query.filter(is_fake=False)
            
            # Likes erstellen und Nachrichten senden
            likes_created = 0
            with transaction.atomic():
                for user in users_query:
                    # Prüfen, ob der Like bereits existiert
                    if not Like.objects.filter(user=fake_user, liked_user=user).exists():
                        # Like erstellen
                        Like.objects.create(user=fake_user, liked_user=user)
                        
                        # Automatische Nachricht senden
                        message_content = f"{fake_user.username} hat dein Profil geliked! 💖"
                        Message.objects.create(
                            sender=fake_user,
                            recipient=user,
                            content=message_content
                        )
                        
                        likes_created += 1
            
            model_admin.message_user(
                request, 
                f"{likes_created} Benutzer wurden erfolgreich geliked.",
                messages.SUCCESS
            )
            return HttpResponseRedirect("../")
    else:
        form = MassLikeForm()
    
    context = {
        'title': 'Massenlike-Funktion',
        'form': form,
        'opts': model_admin.model._meta,
    }
    return render(request, 'admin/mass_like_form.html', context)

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    # --- KORRIGIERT: seeking_gender zu seeking geändert ---
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_fake', 'gender', 'seeking', 'coin_balance', 'assigned_moderator', 'can_use_ai_assist')
    # --- ENDE KORREKTUR ---
    # --- KORRIGIERT: seeking_gender zu seeking geändert ---
    list_filter = UserAdmin.list_filter + ('is_fake', 'can_use_ai_assist', 'is_staff', 'gender', 'seeking') # Filter korrigiert
    # --- ENDE KORREKTUR ---
    # ordering = ('-date_joined',)

    # fieldsets für die Bearbeitungsansicht
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email")}),
        (
            _("Permissions"),
            { "fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions",), },
        ),
        # --- Abschnitt mit unseren Feldern ---
        (_("Zusätzliche Felder & Profil"), {
            "fields": (
                'is_fake',
                'ai_personality_prompt',
                'coin_balance',
                'assigned_moderator',
                'moderator_notes',
                'can_use_ai_assist',
                # --- Profilfelder ---
                'birth_date',
                # --- KORRIGIERT: seeking_gender zu seeking geändert ---
                'gender',
                'seeking', # <--- HIER KORRIGIERT
                # --- ENDE KORREKTUR ---
                'postal_code',
                'city',
                'state',
                'country',
                'about_me',
                # --- ENDE ---
            )
        }),
        # --- Ende ---
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

    # --- add_fieldsets ist weiterhin entfernt ---

    # --- NEU: Admin-Aktion für Massenlikes ---
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('mass-like/', self.admin_site.admin_view(self.mass_like_view), name='accounts_customuser_mass_like'),
        ]
        return custom_urls + urls

    def mass_like_view(self, request):
        return mass_like_view(self, request, self)

    # --- ENDE NEU ---

admin.site.register(CustomUser, CustomUserAdmin)


# --- UserProfileImageAdmin (unverändert) ---
@admin.register(UserProfileImage)
class UserProfileImageAdmin(admin.ModelAdmin):
    # ... (Code bleibt wie gehabt) ...
    list_display = ('user', 'image_thumbnail', 'uploaded_at', 'is_approved')
    list_filter = ('is_approved', 'user__username', 'user__is_fake')
    list_editable = ('is_approved',)
    search_fields = ('user__username',)
    readonly_fields = ('uploaded_at', 'image_thumbnail')
    list_per_page = 50
    actions = ['approve_selected']

    @admin.action(description='Mark selected images as approved')
    def approve_selected(self, request, queryset):
        updated_count = queryset.update(is_approved=True)
        self.message_user(request, f"{updated_count} images were successfully marked as approved.", messages.SUCCESS)

    @admin.display(description='Thumbnail')
    def image_thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 50px;" />', obj.image.url)
        return "No Image"

# --- NEU: LikeAdmin ---
@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'liked_user', 'created_at')
    list_filter = ('user__is_fake', 'created_at')
    search_fields = ('user__username', 'liked_user__username')
    date_hierarchy = 'created_at'
    list_per_page = 50
    
    # --- NEU: Admin-Aktion für Massenlikes ---
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('mass-like/', self.admin_site.admin_view(self.mass_like_view), name='accounts_like_mass_like'),
        ]
        return custom_urls + urls

    def mass_like_view(self, request):
        return mass_like_view(self, request, self)

    # --- ENDE NEU ---

# Ende der Datei accounts/admin.py

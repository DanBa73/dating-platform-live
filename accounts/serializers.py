# accounts/serializers.py (Syntax im SuggestionSerializer KORRIGIERT)

from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer
from .models import CustomUser, UserProfileImage, GenderChoices, Like
from django.utils import timezone
from django.conf import settings

# --- PublicUserSerializer für echte Benutzer ---
class PublicUserSerializer(serializers.ModelSerializer):
    """
    Serializer für öffentliche Benutzerinformationen ohne sensible Felder.
    Wird verwendet, um Informationen an echte Benutzer zu senden.
    """
    profile_picture_url = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'profile_picture_url', 'birth_date', 
                  'postal_code', 'city', 'state', 'country', 'about_me', 
                  'gender', 'seeking']
        read_only_fields = fields
    
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

# --- CustomUserDetailsSerializer ---
class CustomUserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('pk', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'is_fake', 'can_use_ai_assist', 'coin_balance', 'country', 'state', 'city', 'postal_code', 'gender', 'seeking', 'about_me', 'birth_date')
        read_only_fields = ('pk', 'username', 'email', 'is_staff', 'is_fake', 'can_use_ai_assist', 'coin_balance', 'gender', 'seeking', 'country', 'state', 'city', 'postal_code', 'about_me', 'birth_date')

# --- ModeratorNotesSerializer ---
class ModeratorNotesSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['moderator_notes']
        extra_kwargs = { 'moderator_notes': {'required': False, 'allow_blank': True, 'allow_null': True } }

# --- UserProfileImageSerializer ---
class UserProfileImageSerializer(serializers.ModelSerializer):
   class Meta:
        model = UserProfileImage
        fields = ['id', 'user', 'image', 'is_approved', 'uploaded_at']
        read_only_fields = ['id', 'user', 'is_approved', 'uploaded_at']

# --- ProfileSerializer (Mit image_gallery) ---
class ProfileSerializer(serializers.ModelSerializer):
    profile_picture_url = serializers.SerializerMethodField()
    image_gallery = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    coin_balance = serializers.IntegerField(read_only=True)

    class Meta:
        model = CustomUser
        fields = [ 'pk', 'username', 'first_name', 'last_name', 'birth_date', 'postal_code', 'city', 'state', 'country', 'about_me', 'gender', 'seeking', 'profile_picture_url', 'image_gallery', 'is_liked', 'coin_balance' ]
        read_only_fields = fields

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

    def get_image_gallery(self, obj):
        request = self.context.get('request')
        approved_images = obj.profile_images.filter(is_approved=True).order_by('uploaded_at')
        image_urls = []
        for img_obj in approved_images:
            if hasattr(img_obj.image, 'url'):
                if request:
                    image_urls.append(request.build_absolute_uri(img_obj.image.url))
                else:
                    try:
                        media_url = getattr(settings, 'MEDIA_URL', '/media/')
                        image_urls.append(f"{media_url}{img_obj.image.name}")
                    except Exception:
                        pass
        return image_urls
    
    def get_is_liked(self, obj):
        """
        Prüft, ob der aktuelle Benutzer dieses Profil bereits geliked hat.
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Like.objects.filter(user=request.user, liked_user=obj).exists()
        return False

# --- CustomRegisterSerializer (Korrigiert) ---
class CustomRegisterSerializer(RegisterSerializer):
    username = serializers.CharField(required=True, max_length=150)
    email = serializers.EmailField(required=True)
    password1 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    gender = serializers.ChoiceField(choices=GenderChoices.choices, required=False, allow_null=True)
    seeking = serializers.ChoiceField(choices=GenderChoices.choices, required=False, allow_null=True)

    class Meta:
        fields = ('username', 'email', 'password1', 'password2', 'gender', 'seeking') # type: ignore

    def save(self, request):
        user = super().save(request)
        user.gender = self.validated_data.get('gender', None)
        user.seeking = self.validated_data.get('seeking', None)
        update_fields = []
        if user.gender is not None:
            update_fields.append('gender')
        if user.seeking is not None:
            update_fields.append('seeking')
        if update_fields:
            user.save(update_fields=update_fields)
        return user

# --- SuggestionSerializer (KORRIGIERT) ---
class SuggestionSerializer(serializers.ModelSerializer):
    # Felder (unverändert)
    age = serializers.SerializerMethodField()
    profile_picture_url = serializers.SerializerMethodField()
    id = serializers.IntegerField(source='pk', read_only=True)
    username = serializers.CharField(read_only=True)
    city = serializers.CharField(read_only=True)
    state = serializers.CharField(read_only=True)
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'age', 'city', 'state', 'profile_picture_url', 'is_liked']
        read_only_fields = fields # Alle Felder sind nur zum Lesen

    # KORRIGIERT: get_age Methode - Korrekte Einrückung und Logik
    def get_age(self, obj):
        if obj.birth_date:
            try:
                today = timezone.now().date()
                # Korrekte Altersberechnung
                age = today.year - obj.birth_date.year - ((today.month, today.day) < (obj.birth_date.month, obj.birth_date.day))
                return age if age >= 0 else None # Gebe Alter zurück (oder None wenn negativ)
            except Exception:
                # Bei unerwarteten Fehlern (z.B. ungültiges Datum)
                return None
        return None # Kein Alter, wenn kein Geburtsdatum

    # KORRIGIERT: get_profile_picture_url Methode - Korrekte Einrückung
    def get_profile_picture_url(self, obj):
        # Annahme: related_name='profile_images' und UserProfileImage hat 'is_approved' Feld
        first_approved_image = obj.profile_images.filter(is_approved=True).order_by('uploaded_at').first()
        if first_approved_image and hasattr(first_approved_image.image, 'url'):
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(first_approved_image.image.url)
            else:
                # Fallback (weniger wahrscheinlich)
                try:
                    media_url = getattr(settings, 'MEDIA_URL', '/media/')
                    return f"{media_url}{first_approved_image.image.name}"
                except Exception:
                    return None # Im Zweifel nichts zurückgeben
        return None # Kein Bild vorhanden oder URL nicht zugreifbar
    
    def get_is_liked(self, obj):
        """
        Prüft, ob der aktuelle Benutzer dieses Profil bereits geliked hat.
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Like.objects.filter(user=request.user, liked_user=obj).exists()
        return False
# --- ENDE KORREKTUR ---

# --- NEU: LikeSerializer ---
class LikeSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='liked_user.username', read_only=True)
    profile_picture_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Like
        fields = ['id', 'user', 'liked_user', 'created_at', 'username', 'profile_picture_url']
        read_only_fields = ['id', 'created_at', 'username', 'profile_picture_url']
    
    def get_profile_picture_url(self, obj):
        first_approved_image = obj.liked_user.profile_images.filter(is_approved=True).order_by('uploaded_at').first()
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
# --- ENDE NEU ---

# Ende der Datei accounts/serializers.py

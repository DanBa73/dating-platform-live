# accounts/views.py (Korrigierte Einrückung INKLUSIVE Country-Filter)

from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, ListAPIView, DestroyAPIView, RetrieveAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from rest_framework.exceptions import ValidationError, PermissionDenied
from django.db.models import Q
from django.db import transaction

from .models import CustomUser, UserProfileImage, Like
from .serializers import (
    ModeratorNotesSerializer,
    UserProfileImageSerializer,
    ProfileSerializer,
    SuggestionSerializer,
    LikeSerializer
)
from messaging.models import Message
from notifications.models import Notification, NotificationType

# Create your views here.

# --- View für Moderator-Notizen (KORREKT FORMATIERT) ---
class UserNotesView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, user_id):
        target_user = get_object_or_404(CustomUser, pk=user_id)
        serializer = ModeratorNotesSerializer(target_user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, user_id):
        target_user = get_object_or_404(CustomUser, pk=user_id)
        serializer = ModeratorNotesSerializer(instance=target_user, data=request.data, partial=True)
        # Korrekte Einrückung und Struktur:
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# --- View für Profilbild-Upload (Formatiert) ---
class ProfileImageUploadView(CreateAPIView):
    serializer_class = UserProfileImageSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        user = self.request.user
        max_images = 5
        current_image_count = UserProfileImage.objects.filter(user=user).count()
        if current_image_count >= max_images:
            raise ValidationError(f"Upload limit reached ({max_images}).")
        is_approved = user.is_fake
        serializer.save(user=user, is_approved=is_approved)

# --- View zum Auflisten der Profilbilder eines Users (Formatiert) ---
class UserProfileImageViewList(ListAPIView):
    serializer_class = UserProfileImageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        if user_id is None:
            return UserProfileImage.objects.none()
        queryset = UserProfileImage.objects.filter(user__id=user_id, is_approved=True).order_by('uploaded_at')
        return queryset

# --- View zum Löschen eines Profilbildes (Formatiert) ---
class ProfileImageDeleteView(DestroyAPIView):
    queryset = UserProfileImage.objects.all()
    serializer_class = UserProfileImageSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise PermissionDenied("Cannot delete other user's image.")
        super().perform_destroy(instance)

# --- View für die Profil-Detailansicht (KORRIGIERT) ---
class UserProfileDetailView(RetrieveAPIView):
    queryset = CustomUser.objects.filter(is_active=True).prefetch_related('profile_images')
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'
    lookup_url_kwarg = 'user_id'
    
    # NEU: Kontext mit request übergeben
    def get_serializer_context(self):
        context = super().get_serializer_context()
        return context

# --- Pagination Klasse (unverändert) ---
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

# --- SuggestionListView (Mit Country-Filter) ---
class SuggestionListView(ListAPIView):
    serializer_class = SuggestionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        user = self.request.user
        if not user.seeking:
            return CustomUser.objects.none()

        queryset = CustomUser.objects.filter(
            is_active=True,
            gender=user.seeking
        ).exclude(
            pk=user.pk
        )

        filter_country = self.request.query_params.get('country', None) # NEU
        filter_state = self.request.query_params.get('state', None)
        filter_city = self.request.query_params.get('city', None)
        filter_plz = self.request.query_params.get('plz', None)

        if filter_country: # NEU
            queryset = queryset.filter(country__iexact=filter_country) # NEU
        if filter_state:
            queryset = queryset.filter(state__iexact=filter_state)
        if filter_city:
            queryset = queryset.filter(city__iexact=filter_city)
        if filter_plz:
            queryset = queryset.filter(postal_code__startswith=filter_plz)

        queryset = queryset.prefetch_related('profile_images').order_by('?')
        return queryset

# --- ENDE SuggestionListView ---

# --- NEU: LikeView ---
class LikeView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, user_id):
        """
        Erstellt einen Like für einen Benutzer und sendet eine automatische Nachricht.
        """
        user = request.user
        liked_user = get_object_or_404(CustomUser, pk=user_id)
        
        # Prüfen, ob der Benutzer sich selbst liken möchte
        if user.pk == liked_user.pk:
            return Response(
                {"error": "Sie können sich nicht selbst liken."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Prüfen, ob der Like bereits existiert
        like_exists = Like.objects.filter(user=user, liked_user=liked_user).exists()
        if like_exists:
            return Response(
                {"error": "Sie haben dieses Profil bereits geliked."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Like erstellen
        like = Like.objects.create(user=user, liked_user=liked_user)
        
        # Automatische Nachricht senden (ohne Coin-Abzug)
        message_content = f"{user.username} hat dein Profil geliked! 💖"
        message = Message.objects.create(
            sender=user,
            recipient=liked_user,
            content=message_content
        )
        
        # Benachrichtigung erstellen
        Notification.objects.create(
            user=liked_user,
            type=NotificationType.LIKE,
            sender=user,
            content=f"{user.username} hat dein Profil geliked!",
            reference_id=like.id,
            reference_model='Like'
        )
        
        return Response(
            {"success": "Profil erfolgreich geliked und Nachricht gesendet."},
            status=status.HTTP_201_CREATED
        )
    
    def delete(self, request, user_id):
        """
        Entfernt einen Like für einen Benutzer.
        """
        user = request.user
        liked_user = get_object_or_404(CustomUser, pk=user_id)
        
        # Like suchen und löschen
        like = Like.objects.filter(user=user, liked_user=liked_user).first()
        if not like:
            return Response(
                {"error": "Like nicht gefunden."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        like.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# --- NEU: UserLikesListView ---
class UserLikesListView(ListAPIView):
    """
    Listet alle Likes eines Benutzers auf (Favoriten).
    """
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        return Like.objects.filter(user=self.request.user).select_related('liked_user')

# --- NEU: UserReceivedLikesListView ---
class UserReceivedLikesListView(ListAPIView):
    """
    Listet alle Likes auf, die ein Benutzer erhalten hat.
    """
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        return Like.objects.filter(liked_user=self.request.user).select_related('user')

# --- NEU: AdminMassLikeView ---
class AdminMassLikeView(APIView):
    """
    Ermöglicht es Administratoren, mit einem Fake-Profil automatisch alle echten Benutzer 
    mit bestimmten Kriterien zu liken.
    """
    permission_classes = [IsAdminUser]
    
    @transaction.atomic
    def post(self, request):
        fake_user_id = request.data.get('fake_user_id')
        filter_criteria = request.data.get('filter_criteria', {})
        
        if not fake_user_id:
            return Response(
                {"error": "Fake-Benutzer-ID ist erforderlich."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            fake_user = CustomUser.objects.get(pk=fake_user_id, is_fake=True)
        except CustomUser.DoesNotExist:
            return Response(
                {"error": "Fake-Benutzer nicht gefunden."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Benutzer filtern basierend auf den Kriterien
        users_query = CustomUser.objects.filter(is_fake=False, is_active=True)
        
        # Anwenden der Filter
        if 'postal_code_prefix' in filter_criteria:
            prefix = filter_criteria['postal_code_prefix']
            if prefix:
                users_query = users_query.filter(postal_code__startswith=prefix)
        
        if 'state' in filter_criteria:
            state = filter_criteria['state']
            if state:
                users_query = users_query.filter(state__iexact=state)
        
        # Likes erstellen und Nachrichten senden
        likes_created = 0
        for user in users_query:
            # Prüfen, ob der Like bereits existiert
            if not Like.objects.filter(user=fake_user, liked_user=user).exists():
                # Like erstellen
                like = Like.objects.create(user=fake_user, liked_user=user)
                
                # Automatische Nachricht senden
                message_content = f"{fake_user.username} hat dein Profil geliked! 💖"
                message = Message.objects.create(
                    sender=fake_user,
                    recipient=user,
                    content=message_content
                )
                
                # Benachrichtigung erstellen
                Notification.objects.create(
                    user=user,
                    type=NotificationType.LIKE,
                    sender=fake_user,
                    content=f"{fake_user.username} hat dein Profil geliked!",
                    reference_id=like.id,
                    reference_model='Like'
                )
                
                likes_created += 1
        
        return Response(
            {
                "success": f"{likes_created} Benutzer wurden erfolgreich geliked.",
                "likes_created": likes_created
            },
            status=status.HTTP_201_CREATED
        )

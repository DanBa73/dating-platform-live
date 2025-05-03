# accounts/urls.py (FINAL - mit allen accounts-bezogenen URLs)

from django.urls import path
# Importiere ALLE benötigten Views aus der views.py Datei der accounts-App
from .views import (
    UserNotesView,              # Für Moderator-Notizen
    ProfileImageUploadView,     # Für Bild-Upload
    UserProfileImageViewList,   # Für Liste der Bilder eines Users
    ProfileImageDeleteView,     # Für Bild-Löschen
    UserProfileDetailView,      # Für öffentliche Profilansicht
    SuggestionListView,         # Für Partnervorschläge
    LikeView,                   # Für Like-Funktionalität
    UserLikesListView,          # Für Favoriten-Ansicht
    UserReceivedLikesListView,  # Für erhaltene Likes
    AdminMassLikeView           # Für Admin-Massenlikes
)

app_name = 'accounts' # Namespace für diese App

urlpatterns = [
    # === Partnervorschläge ===
    # Erreichbar unter: /api/accounts/suggestions/
    path('suggestions/', SuggestionListView.as_view(), name='user-suggestions'),

    # === Benutzerbezogene Daten (unterhalb von /api/accounts/users/<user_id>/) ===
    # Erreichbar unter: /api/accounts/users/<user_id>/profile/
    path('users/<int:user_id>/profile/', UserProfileDetailView.as_view(), name='user-profile-detail'),
    # Erreichbar unter: /api/accounts/users/<user_id>/profile-images/
    path('users/<int:user_id>/profile-images/', UserProfileImageViewList.as_view(), name='user-profile-image-list'),
    # Erreichbar unter: /api/accounts/users/<user_id>/notes/
    path('users/<int:user_id>/notes/', UserNotesView.as_view(), name='user-notes'),
    # Erreichbar unter: /api/accounts/users/<user_id>/like/
    path('users/<int:user_id>/like/', LikeView.as_view(), name='user-like'),

    # === Profilbilder (allgemein, unterhalb von /api/accounts/profile-images/) ===
    # Erreichbar unter: /api/accounts/profile-images/
    path('profile-images/', ProfileImageUploadView.as_view(), name='profile-image-upload'),
    # Erreichbar unter: /api/accounts/profile-images/<image_pk>/
    path('profile-images/<int:pk>/', ProfileImageDeleteView.as_view(), name='profile-image-delete'),

    # === Likes/Favoriten ===
    # Erreichbar unter: /api/accounts/likes/
    path('likes/', UserLikesListView.as_view(), name='user-likes-list'),
    # Erreichbar unter: /api/accounts/received-likes/
    path('received-likes/', UserReceivedLikesListView.as_view(), name='user-received-likes-list'),
    # Erreichbar unter: /api/accounts/admin/mass-like/
    path('admin/mass-like/', AdminMassLikeView.as_view(), name='admin-mass-like'),
]

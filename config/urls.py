# config/urls.py (Bereinigt und mit include für accounts.urls)

"""
URL configuration for config project.
# ... (Docstring bleibt gleich) ...
"""
from django.contrib import admin
# 'include' wird jetzt verwendet
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# --- Imports für Views aus accounts ENTFERNT ---
# Die Views werden jetzt nur noch in accounts/urls.py benötigt

urlpatterns = [
    # Django Admin Interface
    path('admin/', admin.site.urls),

    # API URLs für unsere Messaging App (unverändert)
    path('api/messaging/', include('messaging.urls')),

    # Auth APIs von dj-rest-auth (unverändert)
    path('api/auth/', include('dj_rest_auth.urls')),
    path('api/auth/registration/', include('dj_rest_auth.registration.urls')),

    # --- NEU: Alle URLs für die accounts-App gebündelt ---
    # Alle URLs, die in accounts/urls.py definiert sind, werden
    # unter dem Präfix 'api/accounts/' verfügbar gemacht.
    # Der Namespace 'accounts' ist optional, aber nützlich.
    path('api/accounts/', include('accounts.urls', namespace='accounts')),
    # --- ENDE accounts-App URLs ---

    # --- NEU: URLs für die notifications-App ---
    path('api/notifications/', include('notifications.urls', namespace='notifications')),
    # --- ENDE notifications-App URLs ---


    # --- URLs für User-spezifische Daten (VERSCHOBEN nach accounts/urls.py) ---
    # path('api/users/<int:user_id>/notes/', UserNotesView.as_view(), name='user-notes'),
    # path('api/users/<int:user_id>/profile-images/', UserProfileImageViewList.as_view(), name='user-profile-image-list'),
    # path('api/users/<int:user_id>/profile/', UserProfileDetailView.as_view(), name='user-profile-detail'),
    # --- ENDE User-spezifische URLs ---

    # --- URLs für Profilbilder (allgemein) (VERSCHOBEN nach accounts/urls.py) ---
    # path('api/profile-images/', ProfileImageUploadView.as_view(), name='profile-image-upload'),
    # path('api/profile-images/<int:pk>/', ProfileImageDeleteView.as_view(), name='profile-image-delete'),
    # --- ENDE Profilbild URLs ---

    # DRF Login/Logout für Browsable API (unverändert)
    path('api-auth/', include('rest_framework.urls')),
]

# Media Files im Development-Modus ausliefern (unverändert)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Ende der Datei config/urls.py

# config/urls.py (Mit React index.html Serving)

"""
URL configuration for config project.
# ... (Docstring bleibt gleich) ...
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
# --- NEU: Import für TemplateView ---
from django.views.generic import TemplateView
# --- ENDE NEU ---


urlpatterns = [
    # --- NEU: Pfad für die React App index.html ---
    # Dieser Pfad fängt alle Anfragen ab, die nicht zu API oder Admin gehören
    # und liefert die index.html aus. React Router übernimmt dann das Routing im Frontend.
    # Wichtig: Dieser Pfad sollte NACH spezifischeren Pfaden wie 'admin/' oder 'api/' stehen,
    # aber wir setzen ihn oft nach vorne zur Verdeutlichung des Catch-All für das Frontend.
    # Django sucht 'index.html' in den Template-Verzeichnissen bzw. über den Staticfiles Finder
    # nach collectstatic.
    # UPDATE: Es ist oft sicherer, diesen Catch-All weiter unten zu platzieren,
    # damit spezifische URLs wie /admin/ Vorrang haben. Wir verschieben ihn nach unten.

    # Django Admin Interface
    path('admin/', admin.site.urls),

    # API URLs für unsere Messaging App (unverändert)
    path('api/messaging/', include('messaging.urls')),

    # Auth APIs von dj-rest-auth (unverändert)
    path('api/auth/', include('dj_rest_auth.urls')),
    path('api/auth/registration/', include('dj_rest_auth.registration.urls')),

    # --- Alle URLs für die accounts-App gebündelt ---
    path('api/accounts/', include('accounts.urls', namespace='accounts')),

    # --- URLs für die notifications-App ---
    path('api/notifications/', include('notifications.urls', namespace='notifications')),

    # --- URLs für User-spezifische Daten (VERSCHOBEN nach accounts/urls.py) ---
    # ... (auskommentierte Pfade bleiben) ...

    # --- URLs für Profilbilder (allgemein) (VERSCHOBEN nach accounts/urls.py) ---
    # ... (auskommentierte Pfade bleiben) ...

    # DRF Login/Logout für Browsable API (unverändert)
    path('api-auth/', include('rest_framework.urls')),

    # --- NEU: Pfad für die React App index.html (Bessere Position: nach API-Pfaden) ---
    # Fängt die Root-URL ab und liefert die index.html für die React App
    path('', TemplateView.as_view(template_name='index.html'), name='react-app'),

    # Optional: Ein Catch-All für React-Router, falls Deep-Links unterstützt werden sollen.
    # Muss als ALLERLETZTES stehen. Requires re_path from django.urls
    # from django.urls import re_path
    # re_path(r'^(?!api/|admin/|media/).*$', TemplateView.as_view(template_name='index.html'), name='react-catchall'),

]

# Media Files im Development-Modus ausliefern (unverändert)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Ende der Datei config/urls.py
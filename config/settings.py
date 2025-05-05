# config/settings.py (Mit Custom Account Adapter und STATICFILES_DIRS)

"""
Django settings for config project.
# ... (Docstring) ...
"""

from pathlib import Path
import os
import dj_database_url # <--- Sicherstellen, dass der Import da ist
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
# Lade .env nur, wenn die Datei existiert (wichtig für Produktionsumgebungen wie Render, die .env nicht direkt nutzen)
dotenv_path = os.path.join(BASE_DIR, '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

# Wichtige Umgebungsvariablen
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-fallback-key-if-not-set-{}'.format(hash(os.times()))) # Sicherer Fallback, wenn Env Var fehlt
# WICHTIG: Für Produktion UNBEDINGT DEBUG=False in den Env Vars setzen!
DEBUG = os.getenv('DEBUG', 'False') == 'True' # Holt aus Env Var, Default ist False
# ALLOWED_HOSTS aus Env Var lesen, Komma-getrennt
ALLOWED_HOSTS_STRING = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1') # Default für lokal
ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS_STRING.split(',') if host.strip()] # Leere Einträge vermeiden

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin', 'django.contrib.auth', 'django.contrib.contenttypes',
    'django.contrib.sessions', 'django.contrib.messages', 'django.contrib.staticfiles',
    'django.contrib.sites',
    # Third-party apps
    'rest_framework', 'rest_framework.authtoken',
    'allauth', 'allauth.account', 'allauth.socialaccount',
    'dj_rest_auth', 'dj_rest_auth.registration',
    'corsheaders',
    'background_task', # Hintergrund-Tasks
    # Your apps
    'accounts', 'messaging', 'notifications',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # Whitenoise für Static Files (oft nützlich hinter Gunicorn) - Optional, falls gebraucht
    # 'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware', # CorsMiddleware hinzugefügt
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware', # allauth Middleware hinzugefügt
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [ {
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
        ],
    },
}, ]

WSGI_APPLICATION = 'config.wsgi.application'

# --- NEUE Datenbankkonfiguration (nutzt dj-database-url) ---
DATABASES = {
    'default': dj_database_url.config(
        conn_max_age=600, # Optional: Connection Pooling
        default=os.getenv('DATABASE_URL') # Liest die DATABASE_URL von Render (oder .env lokal)
    )
}
# Fallback auf SQLite, wenn DATABASE_URL nicht gesetzt ist (z.B. für lokale Tests ohne .env)
if not DATABASES['default'].get('ENGINE'):
     DATABASES['default'] = {
         'ENGINE': 'django.db.backends.sqlite3',
         'NAME': BASE_DIR / 'db.sqlite3',
     }
# --- ENDE NEUE Datenbankkonfiguration ---

# Password validation
AUTH_PASSWORD_VALIDATORS = [ { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', }, { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', }, { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', }, { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', }, ]

# Custom User Model
AUTH_USER_MODEL = 'accounts.CustomUser'

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files & Media files
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles' # HINZUGEFÜGT für collectstatic

# --- NEU: Pfad zum React Build-Ordner ---
STATICFILES_DIRS = [
    BASE_DIR / 'frontend/dist',
]
# --- ENDE NEU ---

# Optional: Whitenoise Konfiguration für statische Dateien direkt über Gunicorn/Django
# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- allauth / dj-rest-auth settings ---
SITE_ID = 1
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend' # Für Entwicklung/Test
ACCOUNT_EMAIL_VERIFICATION = 'none' # Keine E-Mail-Verifizierung (vereinfacht)
ACCOUNT_AUTHENTICATION_METHOD = 'username_email' # Login mit User oder E-Mail
ACCOUNT_EMAIL_REQUIRED = True

ACCOUNT_FORMS = {
    'signup': 'allauth.account.forms.SignupForm', # Standard-Signup-Form
}

# Custom Account Adapter verwenden
ACCOUNT_ADAPTER = 'accounts.adapter.CustomAccountAdapter'

# CORS settings (Anpassen für Produktion!)
# Lese aus Env Var oder setze sinnvolle Defaults
CORS_ALLOWED_ORIGINS_STRING = os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:5173,http://127.0.0.1:5173')
CORS_ALLOWED_ORIGINS = [origin.strip() for origin in CORS_ALLOWED_ORIGINS_STRING.split(',') if origin.strip()]
# Füge Render-URL und Custom Domain hinzu, wenn nicht schon über Env Var gesetzt
render_hostname = os.getenv('RENDER_EXTERNAL_HOSTNAME') # Render setzt diese automatisch
if render_hostname and render_hostname not in ALLOWED_HOSTS:
     ALLOWED_HOSTS.append(render_hostname) # Erlaube Zugriff über die .onrender.com-URL
# Stelle sicher, dass CORS auch die Render-URL erlaubt, falls nötig
# if render_hostname and f"https://{render_hostname}" not in CORS_ALLOWED_ORIGINS:
#      CORS_ALLOWED_ORIGINS.append(f"https://{render_hostname}")
#      CSRF_TRUSTED_ORIGINS.append(f"https://{render_hostname}")

# Vertrauenswürdige Origins für CSRF (wichtig für Formulare/Logins)
CSRF_TRUSTED_ORIGINS_STRING = os.getenv('CSRF_TRUSTED_ORIGINS', 'http://localhost:5173,http://127.0.0.1:5173')
CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in CSRF_TRUSTED_ORIGINS_STRING.split(',') if origin.strip()]
# Füge Render-URL und Custom Domain hinzu
# if render_hostname and f"https://{render_hostname}" not in CSRF_TRUSTED_ORIGINS:
#      CSRF_TRUSTED_ORIGINS.append(f"https://{render_hostname}")


# Django REST Framework Einstellungen
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication', # Token-Auth für APIs
        'rest_framework.authentication.SessionAuthentication', # Session-Auth für Browser
    ],
}

# --- dj-rest-auth spezifische Einstellungen ---
REST_AUTH = {
    'USER_DETAILS_SERIALIZER': 'accounts.serializers.CustomUserDetailsSerializer',
    'REGISTER_SERIALIZER': 'accounts.serializers.CustomRegisterSerializer',
}

# OpenAI API Key
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# --- AI Auto Reply Delay Settings ---
AI_AUTO_REPLY_MIN_DELAY_SECONDS = int(os.getenv('AI_AUTO_REPLY_MIN_DELAY_SECONDS', '30'))
AI_AUTO_REPLY_MAX_DELAY_SECONDS = int(os.getenv('AI_AUTO_REPLY_MAX_DELAY_SECONDS', '300'))

# Ende der Datei config/settings.py
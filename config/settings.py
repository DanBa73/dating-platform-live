# config/settings.py (Mit Custom Account Adapter)

"""
Django settings for config project.
# ... (Docstring) ...
"""

from pathlib import Path
import os
import dj_database_url # Sicherstellen, dass dies importiert ist
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(os.path.join(BASE_DIR, '.env')) # Lädt .env

# Wichtige Umgebungsvariablen
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-default-key-for-development') # Holt aus Env Var, mit unsicherem Default
DEBUG = os.getenv('DEBUG', 'False') == 'True' # Holt aus Env Var, Default ist False
ALLOWED_HOSTS_STRING = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1')
ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS_STRING.split(',')] # Holt aus Env Var, Default für lokal

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

# Database
# Verwende dj-database-url für die Datenbankkonfiguration aus DATABASE_URL Env Var
DATABASE_URL = os.getenv('DATABASE_URL')

# Standard-Fallback (z.B. für lokale Entwicklung ohne gesetzte DATABASE_URL)
# Optional: Hier ENGINE und PORT an lokale MariaDB/MySQL anpassen, falls gewünscht
default_db_config = {
    'ENGINE': 'django.db.backends.sqlite3', # Sicherer Fallback auf SQLite
    'NAME': BASE_DIR / 'db.sqlite3',
    # 'ENGINE': 'django.db.backends.mysql', # Wenn lokal auch MariaDB benutzt wird
    # 'NAME': os.getenv('DATABASE_NAME', 'dating_platform_db_local'),
    # 'USER': os.getenv('DATABASE_USER', 'local_user'),
    # 'PASSWORD': os.getenv('DATABASE_PASSWORD', ''),
    # 'HOST': os.getenv('DATABASE_HOST', 'localhost'),
    # 'PORT': os.getenv('DATABASE_PORT', '3306'),
}

DATABASES = {
    'default': dj_database_url.config(default=DATABASE_URL, conn_max_age=600) if DATABASE_URL else default_db_config
}


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
# Erlaube Anfragen von deinem Frontend (z.B. localhost für Entwicklung, deine Domain für Produktion)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173", # Lokales React Frontend
    "http://127.0.0.1:5173", # Lokales React Frontend
    # --- FÜR PRODUKTION HINZUFÜGEN ---
    # "https://flirtenundtreffen.de",
    # "https://www.flirtenundtreffen.de",
    # "https://flirtundtreffen.onrender.com", # Render Standard-Domain
]
# Vertrauenswürdige Origins für CSRF (wichtig für Formulare/Logins)
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    # --- FÜR PRODUKTION HINZUFÜGEN ---
    # "https://flirtenundtreffen.de",
    # "https://www.flirtenundtreffen.de",
    # "https://flirtundtreffen.onrender.com",
]

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
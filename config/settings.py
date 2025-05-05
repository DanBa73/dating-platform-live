# config/settings.py (Mit Custom Account Adapter)

"""
Django settings for config project.
# ... (Docstring) ...
"""

from pathlib import Path
import os
import dj_database_url
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(os.path.join(BASE_DIR, '.env'))

# Wichtige Umgebungsvariablen
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-default-key-for-development')
DEBUG = os.getenv('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

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

MIDDLEWARE = [ # ... (Middleware unverändert) ...
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [ { # ... (Template Settings unverändert) ...
    'BACKEND': 'django.template.backends.django.DjangoTemplates','DIRS': [], 'APP_DIRS': True,
    'OPTIONS': {'context_processors': ['django.template.context_processors.request','django.contrib.auth.context_processors.auth','django.contrib.messages.context_processors.messages',],},
}, ]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
# Verwende dj-database-url für die Datenbankkonfiguration
# Dies unterstützt die DATABASE_URL-Umgebungsvariable, die von Render.com bereitgestellt wird
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL)
    }
else:
    # Fallback für lokale Entwicklung
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DATABASE_NAME', 'dating_platform_db'),
            'USER': os.getenv('DATABASE_USER', 'postgres'),
            'PASSWORD': os.getenv('DATABASE_PASSWORD', ''),
            'HOST': os.getenv('DATABASE_HOST', 'localhost'),
            'PORT': os.getenv('DATABASE_PORT', '5432'),
        }
    }


# Password validation
AUTH_PASSWORD_VALIDATORS = [ { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', }, { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', }, { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', }, { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', }, ]

# Custom User Model
AUTH_USER_MODEL = 'accounts.CustomUser'

# Internationalization
LANGUAGE_CODE = 'en-us'; TIME_ZONE = 'UTC'; USE_I18N = True; USE_TZ = True

# Static files & Media files
STATIC_URL = 'static/'
MEDIA_URL = '/media/'; MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- allauth / dj-rest-auth settings ---
SITE_ID = 1
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
ACCOUNT_EMAIL_VERIFICATION = 'none'
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
ACCOUNT_EMAIL_REQUIRED = True

ACCOUNT_FORMS = {
    'signup': 'allauth.account.forms.SignupForm',
}

# --- NEU: Custom Account Adapter verwenden ---
ACCOUNT_ADAPTER = 'accounts.adapter.CustomAccountAdapter'
# --- ENDE NEU ---

# TODO: Veraltete Einstellungen später ersetzen
# ACCOUNT_LOGIN_METHODS = {'username', 'email'}
# ACCOUNT_SIGNUP_FIELDS = ['email*', 'username*', 'password1*', 'password2*']


# CORS settings
CORS_ALLOWED_ORIGINS = [ "http://localhost:5173", "http://127.0.0.1:5173", ]
CSRF_TRUSTED_ORIGINS = [ "http://localhost:5173", "http://127.0.0.1:5173", ]

# Django REST Framework Einstellungen
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
}

# --- dj-rest-auth spezifische Einstellungen ---
REST_AUTH = {
    'USER_DETAILS_SERIALIZER': 'accounts.serializers.CustomUserDetailsSerializer',
    # WICHTIG: Den Custom Serializer lassen wir aktiv, da er die Felder
    # gender/seeking definiert, damit sie in form.cleaned_data verfügbar sind,
    # auch wenn die eigentliche Speicherlogik jetzt im Adapter liegt.
    'REGISTER_SERIALIZER': 'accounts.serializers.CustomRegisterSerializer', # Bleibt AKTIV
}

# OpenAI API Key
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# --- AI Auto Reply Delay Settings ---
AI_AUTO_REPLY_MIN_DELAY_SECONDS = int(os.getenv('AI_AUTO_REPLY_MIN_DELAY_SECONDS', '30'))
AI_AUTO_REPLY_MAX_DELAY_SECONDS = int(os.getenv('AI_AUTO_REPLY_MAX_DELAY_SECONDS', '300'))


# Ende der Datei config/settings.py

from pathlib import Path
from dotenv import load_dotenv
import os
import dj_database_url  # Essential for professional database switching

# ----------------------------------------------------------------
# BASE CONFIGURATION
# ----------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# SECURITY: Never keep the real key in your code!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-fallback-key-change-this')

# SECURITY: DEBUG must be False in production
DEBUG = os.getenv('DEBUG', 'True') == 'True'

# Networking: Define which IPs/Domains can talk to this app
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '127.0.0.1,localhost').split(',')
if not DEBUG:
    # Allows Render/Railway domains
    ALLOWED_HOSTS.append('.onrender.com')
    ALLOWED_HOSTS.append('.railway.app')

# ----------------------------------------------------------------
# APPLICATION DEFINITION
# ----------------------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'planner',
    'whitenoise.runserver_nostatic', # Helps serving static files during dev
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Layer for serving premium CSS/Images
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], # For global templates
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# ----------------------------------------------------------------
# DATABASE: Professional Auto-Switching
# ----------------------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# This logic switches to PostgreSQL automatically on Render/Railway
db_from_env = dj_database_url.config(conn_max_age=600)
if db_from_env:
    DATABASES['default'].update(db_from_env)

# ----------------------------------------------------------------
# STATIC & MEDIA FILES (THE "ELITE" LOOK)
# ----------------------------------------------------------------
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles' # Where collectstatic will dump files
STATICFILES_DIRS = [
    BASE_DIR / "planner/static",
]

# Optimize static files (compression)
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ----------------------------------------------------------------
# EXTERNAL API KEYS
# ----------------------------------------------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ----------------------------------------------------------------
# DEFAULTS
# ----------------------------------------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
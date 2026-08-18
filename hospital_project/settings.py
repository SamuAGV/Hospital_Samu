"""
Django settings for hospital_project project.
"""

import os
import certifi
from pathlib import Path
from dotenv import load_dotenv
import pymongo

# Cargar variables de entorno
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-change-me-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party apps
    'crispy_forms',
    'crispy_bootstrap5',
    
    # Local apps
    'apps.core',
    'apps.patients',
    'apps.appointments',
    'apps.consultations',
    'apps.hospitalizations',
    'apps.emergency',
    'apps.laboratory',
    'apps.pharmacy',
    'apps.specialties',
    'apps.analytics',
    'apps.machine_learning',
    'apps.users',
    'apps.reports',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'hospital_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.core.context_processors.mongodb_status',
            ],
        },
    },
]

WSGI_APPLICATION = 'hospital_project.wsgi.application'

# ============================================================
# DATABASE - Configuración para Django (SQLite para sesiones)
# ============================================================
# Django necesita una base de datos SQL para sesiones y autenticación
# Usamos SQLite que es ligera y no requiere configuración adicional
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ============================================================
# MONGODB - Configuración para datos de la aplicación
# ============================================================
MONGO_URI = os.getenv('MONGO_URI')
MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', 'medinsight_hospital')

# Connection to MongoDB con certifi para SSL
try:
    if MONGO_URI and 'mongodb+srv' in MONGO_URI:
        # Conexión a MongoDB Atlas
        mongo_client = pymongo.MongoClient(
            MONGO_URI,
            tlsCAFile=certifi.where(),
            serverSelectionTimeoutMS=10000
        )
    else:
        # Conexión local (sin SSL)
        mongo_client = pymongo.MongoClient(
            MONGO_URI or 'mongodb://localhost:27017/',
            serverSelectionTimeoutMS=10000
        )
    
    # Probar conexión
    mongo_client.admin.command('ping')
    mongo_db = mongo_client[MONGO_DB_NAME]
    MONGO_CONNECTED = True
    print(f"✅ Conectado a MongoDB: {MONGO_DB_NAME}")
except Exception as e:
    MONGO_CONNECTED = False
    print(f"❌ Error al conectar a MongoDB: {e}")
    print("Verifica tu conexión a Internet y las credenciales en .env")
    # Crear una conexión dummy para evitar errores
    mongo_client = None
    mongo_db = None

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'es-mx'
TIME_ZONE = 'America/Mexico_City'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static'] if (BASE_DIR / 'static').exists() else []
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Login/Logout URLs
LOGIN_URL = '/users/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/users/login/'

# Messages
from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.DEBUG: 'alert-secondary',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}

# Session configuration (usar SQLite para sesiones)
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
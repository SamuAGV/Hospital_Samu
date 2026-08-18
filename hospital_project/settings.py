"""
Django settings for hospital_project project.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-change-me-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# ============================================================
# ALLOWED_HOSTS - Configuración para Vercel y desarrollo
# ============================================================
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Detectar si estamos en Vercel
IS_VERCEL = os.environ.get('VERCEL', False)
IS_BUILDING = 'build' in sys.argv or 'collectstatic' in sys.argv

# Agregar dominios de Vercel automáticamente
if IS_VERCEL:
    # Dominios de Vercel
    vercel_url = os.environ.get('VERCEL_URL', '')
    if vercel_url:
        ALLOWED_HOSTS.append(vercel_url)
        ALLOWED_HOSTS.append(f'{vercel_url}.vercel.app')
    
    deployment_url = os.environ.get('VERCEL_DEPLOYMENT_URL', '')
    if deployment_url:
        ALLOWED_HOSTS.append(deployment_url)
    
    # Permitir todos los subdominios de vercel.app
    ALLOWED_HOSTS.append('.vercel.app')
    
    # Tu dominio específico
    ALLOWED_HOSTS.append('hospital-samu.vercel.app')

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

# Variables globales para MongoDB
mongo_client = None
mongo_db = None
MONGO_CONNECTED = False

# Solo intentar conectar si no estamos en Vercel o en entorno de construcción
if not IS_VERCEL and not IS_BUILDING:
    try:
        import certifi
        import pymongo
        
        if MONGO_URI:
            if 'mongodb+srv' in MONGO_URI:
                # Conexión a MongoDB Atlas
                mongo_client = pymongo.MongoClient(
                    MONGO_URI,
                    tlsCAFile=certifi.where(),
                    serverSelectionTimeoutMS=10000
                )
            else:
                # Conexión local
                mongo_client = pymongo.MongoClient(
                    MONGO_URI,
                    serverSelectionTimeoutMS=10000
                )
            
            # Probar conexión
            if mongo_client:
                mongo_client.admin.command('ping')
                mongo_db = mongo_client[MONGO_DB_NAME]
                MONGO_CONNECTED = True
                # Solo imprimir en desarrollo, no en producción
                if not IS_VERCEL:
                    print(f"Conectado a MongoDB: {MONGO_DB_NAME}")
    except Exception as e:
        # Silenciar errores en producción
        if not IS_VERCEL:
            print(f"Error al conectar a MongoDB: {e}")
        MONGO_CONNECTED = False
        mongo_client = None
        mongo_db = None

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
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

# ============================================================
# CONFIGURACIÓN ADICIONAL PARA PRODUCCIÓN EN VERCEL
# ============================================================

# Configuración de seguridad para producción
if IS_VERCEL:
    # Forzar HTTPS en producción
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    
    # Headers de seguridad
    SECURE_HSTS_SECONDS = 31536000  # 1 año
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    
    # Cookies seguras
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    
    # Prevenir que el navegador adivine el tipo de contenido
    SECURE_CONTENT_TYPE_NOSNIFF = True
    
    # Política de referencia
    SECURE_REFERRER_POLICY = 'same-origin'

# Configuración para servir archivos estáticos en Vercel
if IS_VERCEL:
    # En Vercel, los archivos estáticos se sirven desde /staticfiles
    STATIC_URL = '/static/'
    STATIC_ROOT = '/tmp/staticfiles'  # Vercel usa /tmp para escritura
else:
    STATIC_ROOT = BASE_DIR / 'staticfiles'

# Logging en producción (opcional pero recomendado)
if not DEBUG:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
            },
        },
        'root': {
            'handlers': ['console'],
            'level': 'WARNING',
        },
        'loggers': {
            'django': {
                'handlers': ['console'],
                'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
                'propagate': False,
            },
        },
    }
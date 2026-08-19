"""
Django settings for hospital_project project.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import hashlib
import json

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
    vercel_url = os.environ.get('VERCEL_URL', '')
    if vercel_url:
        ALLOWED_HOSTS.append(vercel_url)
        ALLOWED_HOSTS.append(f'{vercel_url}.vercel.app')
    
    deployment_url = os.environ.get('VERCEL_DEPLOYMENT_URL', '')
    if deployment_url:
        ALLOWED_HOSTS.append(deployment_url)
    
    ALLOWED_HOSTS.append('.vercel.app')
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
    'apps.core.middleware.ErrorLoggingMiddleware',  # 👈 AGREGAR ESTO AL FINAL
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
# MONGODB - Configuración principal
# ============================================================
MONGO_URI = os.getenv('MONGO_URI')
MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', 'medinsight_hospital')

# Variables globales para MongoDB
mongo_client = None
mongo_db = None
MONGO_CONNECTED = False

# Intentar conectar a MongoDB
if MONGO_URI:
    try:
        import certifi
        import pymongo
        
        if 'mongodb+srv' in MONGO_URI:
            mongo_client = pymongo.MongoClient(
                MONGO_URI,
                tlsCAFile=certifi.where(),
                serverSelectionTimeoutMS=10000
            )
        else:
            mongo_client = pymongo.MongoClient(
                MONGO_URI,
                serverSelectionTimeoutMS=10000
            )
        
        if mongo_client:
            mongo_client.admin.command('ping')
            mongo_db = mongo_client[MONGO_DB_NAME]
            MONGO_CONNECTED = True
            
            # Crear índices para usuarios
            if MONGO_CONNECTED:
                users_collection = mongo_db['users']
                users_collection.create_index('username', unique=True)
                users_collection.create_index('email', unique=True)
                
            if not IS_VERCEL:
                print(f"Conectado a MongoDB: {MONGO_DB_NAME}")
    except Exception as e:
        if not IS_VERCEL:
            print(f"Error al conectar a MongoDB: {e}")
        MONGO_CONNECTED = False
        mongo_client = None
        mongo_db = None

# ============================================================
# DATABASE - Usar SQLite solo para sesiones (en memoria en Vercel)
# ============================================================
if IS_VERCEL:
    import dj_database_url
    
    # Usar PostgreSQL desde la variable DATABASE_URL
    DATABASES = {
        'default': dj_database_url.config(
            default=os.getenv('DATABASE_URL'),
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
    
    # Configuración adicional para producción
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
else:
    # Desarrollo: SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }



# Usar sesiones basadas en cache para evitar escritura en disco
# ============================================================
# SESSION CONFIGURATION - Usar base de datos para sesiones
# ============================================================
if IS_VERCEL:
    # En Vercel, usar la base de datos (SQLite en memoria o PostgreSQL)
    # pero con persistencia de sesión
    SESSION_ENGINE = 'django.contrib.sessions.backends.db'
    SESSION_COOKIE_AGE = 86400  # 24 horas
    SESSION_SAVE_EVERY_REQUEST = True
    SESSION_EXPIRE_AT_BROWSER_CLOSE = False
    
    # Configurar cache para otros usos
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        }
    }
else:
    SESSION_ENGINE = 'django.contrib.sessions.backends.db'
    SESSION_COOKIE_AGE = 1209600  # 2 semanas

# ============================================================
# AUTHENTICATION - Usar backend personalizado de MongoDB
# ============================================================
AUTHENTICATION_BACKENDS = [
    'apps.users.backends.MongoDBBackend',
    #'django.contrib.auth.backends.ModelBackend',  
]

# Password validation (para mantener compatibilidad)
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
STATIC_ROOT = '/tmp/staticfiles' if IS_VERCEL else BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = '/tmp/media' if IS_VERCEL else BASE_DIR / 'media'

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

# ============================================================
# CONFIGURACIÓN ADICIONAL PARA PRODUCCIÓN EN VERCEL
# ============================================================

if IS_VERCEL:
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_REFERRER_POLICY = 'same-origin'
    
    SESSION_COOKIE_AGE = 86400  # 24 horas
    SESSION_SAVE_EVERY_REQUEST = True

# Logging
if not DEBUG:
    LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} - {name}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'apps.core': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'apps.users': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}


# ============================================================
# EXPORTAR VARIABLES DE MONGODB PARA ACCESO GLOBAL
# ============================================================
# Esto permite acceder a mongo_db y mongo_client desde cualquier parte
# a través de settings.MONGO_DB, settings.MONGO_CLIENT, etc.
MONGO_CLIENT = mongo_client
MONGO_DB = mongo_db

# Configuración de logging para Vercel
if IS_VERCEL:
    LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} - {name}: {message}',
            'style': '{',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'apps.users.backends': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps.users.views': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.contrib.auth': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# ============================================================
# CONFIGURACIÓN PARA VERCEL
# ============================================================
if IS_VERCEL:
    print("Ejecutando en Vercel...", file=sys.stderr)
    
    # Forzar migraciones en el inicio
    try:
        from django.db import connection
        from django.core.management import call_command
        
        # Verificar si la tabla auth_user existe
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='auth_user'")
            table_exists = cursor.fetchone()
        
        if not table_exists:
            print("Ejecutando migraciones en settings...", file=sys.stderr)
            call_command('migrate', interactive=False, verbosity=1)
            print("Migraciones completadas en settings", file=sys.stderr)
            
            # Sincronizar usuarios de MongoDB
            if MONGO_CONNECTED and MONGO_DB is not None:
                print("Sincronizando usuarios en settings...", file=sys.stderr)
                db = MONGO_DB
                users_collection = db['users']
                from django.contrib.auth.models import User
                
                mongo_users = list(users_collection.find({}))
                for user_data in mongo_users:
                    username = user_data.get('username')
                    if username:
                        user, created = User.objects.get_or_create(
                            username=username,
                            defaults={
                                'email': user_data.get('email', ''),
                                'first_name': user_data.get('first_name', ''),
                                'last_name': user_data.get('last_name', ''),
                                'is_active': user_data.get('is_active', True),
                                'is_staff': user_data.get('is_staff', False),
                                'is_superuser': user_data.get('is_superuser', False),
                            }
                        )
                        if created:
                            user.set_unusable_password()
                            user.save()
                            print(f'Usuario sincronizado: {username}', file=sys.stderr)
                print(f'Total usuarios: {User.objects.count()}', file=sys.stderr)
    except Exception as e:
        print(f"⚠️ Error en configuración de Vercel: {e}", file=sys.stderr)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} - {name}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',  # Cambiar a DEBUG para ver todo
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'apps.core': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'apps.machine_learning': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

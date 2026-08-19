# apps/users/backends.py
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from django.conf import settings
from .utils import verify_password
import logging

logger = logging.getLogger(__name__)

class MongoDBBackend(BaseBackend):
    
    def authenticate(self, request, username=None, password=None):
        logger.info(f"🔐 Autenticando: {username}")
        
        if not settings.MONGO_CONNECTED or settings.MONGO_DB is None:
            logger.error("❌ MongoDB no conectado")
            return None
        
        try:
            db = settings.MONGO_DB
            users_collection = db['users']
            
            user_data = users_collection.find_one({
                '$or': [{'username': username}, {'email': username}]
            })
            
            if not user_data:
                logger.warning(f"❌ Usuario no encontrado: {username}")
                return None
            
            # Verificar contraseña
            stored_password = user_data.get('password', '')
            if not verify_password(password, stored_password):
                logger.warning(f"❌ Contraseña incorrecta para: {username}")
                return None
            
            # Crear o obtener usuario de Django (sin verificar tablas)
            try:
                user = User.objects.get(username=user_data['username'])
            except User.DoesNotExist:
                user = User(
                    username=user_data['username'],
                    email=user_data.get('email', ''),
                    first_name=user_data.get('first_name', ''),
                    last_name=user_data.get('last_name', ''),
                    is_active=user_data.get('is_active', True),
                    is_staff=user_data.get('is_staff', False),
                    is_superuser=user_data.get('is_superuser', False),
                )
                user.set_unusable_password()
                user.save()
                logger.info(f"🆕 Usuario Django creado: {username}")
            
            logger.info(f"✅ Autenticación exitosa para: {user.username}")
            return user
            
        except Exception as e:
            logger.error(f"💥 Error en autenticación: {e}")
            return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
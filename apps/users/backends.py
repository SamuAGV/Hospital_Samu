# apps/users/backends.py
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from django.conf import settings
from .utils import hash_password, verify_password
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class MongoDBBackend(BaseBackend):
    """
    Backend de autenticación que usa MongoDB directamente.
    """
    
    def authenticate(self, request, username=None, password=None):
        logger.info("=" * 50)
        logger.info(f"Intento de autenticación para: {username}")
        logger.info(f"MONGO_CONNECTED: {settings.MONGO_CONNECTED}")
        logger.info(f"MONGO_DB is None: {settings.MONGO_DB is None}")
        
        if not settings.MONGO_CONNECTED or settings.MONGO_DB is None:
            logger.error("MongoDB NO está conectado")
            return None
        
        try:
            db = settings.MONGO_DB
            users_collection = db['users']
            
            # Buscar usuario por username o email
            user_data = users_collection.find_one({
                '$or': [
                    {'username': username},
                    {'email': username}
                ]
            })
            
            if not user_data:
                logger.warning(f"Usuario no encontrado: {username}")
                return None
            
            logger.info(f"Usuario encontrado: {user_data.get('username')}")
            
            # Verificar contraseña usando la función consistente
            stored_password = user_data.get('password', '')
            
            # Intentar verificar con diferentes métodos
            password_valid = False
            
            # Método 1: Verificación estándar
            if verify_password(password, stored_password):
                password_valid = True
                logger.info("Contraseña válida (método estándar)")
            
            # Método 2: Si falla, intentar con hasheo directo
            if not password_valid:
                hashed_input = hash_password(password)
                if hashed_input == stored_password:
                    password_valid = True
                    logger.info("Contraseña válida (método directo)")
            
            # Método 3: Si aún falla, verificar si la contraseña está sin hashear (solo para desarrollo)
            if not password_valid and password == stored_password:
                # Actualizar a hasheado
                new_hash = hash_password(password)
                users_collection.update_one(
                    {'_id': user_data['_id']},
                    {'$set': {'password': new_hash}}
                )
                password_valid = True
                logger.info("Contraseña actualizada de plano a hasheado")
            
            if password_valid:
                logger.info("Autenticación exitosa")
                
                # Crear o obtener usuario de Django
                try:
                    user = User.objects.get(username=user_data['username'])
                    logger.info("Usuario de Django recuperado")
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
                    logger.info("Usuario de Django creado")
                
                # Actualizar último acceso
                users_collection.update_one(
                    {'_id': user_data['_id']},
                    {'$set': {'last_login': datetime.now().isoformat()}}
                )
                
                return user
            else:
                logger.warning(f"Contraseña incorrecta para: {username}")
                logger.info(f"Hash almacenado: {stored_password[:20]}...")
                logger.info(f"Hash generado: {hash_password(password)[:20]}...")
                return None
                
        except Exception as e:
            logger.error(f"Error en autenticación: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
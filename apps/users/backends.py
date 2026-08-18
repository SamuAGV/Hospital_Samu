# apps/users/backends.py
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from django.conf import settings
import hashlib
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class MongoDBBackend(BaseBackend):
    """
    Backend de autenticación que usa MongoDB directamente.
    """
    
    def authenticate(self, request, username=None, password=None):
        # Log para depuración
        logger.info(f"Intento de autenticación para: {username}")
        
        # Verificar conexión a MongoDB
        if not settings.MONGO_CONNECTED or settings.MONGO_DB is None:
            logger.error("MongoDB no está conectado o no disponible")
            logger.error(f"MONGO_CONNECTED: {settings.MONGO_CONNECTED}")
            logger.error(f"MONGO_DB: {settings.MONGO_DB}")
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
            
            if user_data:
                logger.info(f"Usuario encontrado: {user_data.get('username')}")
                
                # Verificar contraseña (hashed)
                hashed_password = hashlib.sha256(password.encode()).hexdigest()
                
                if user_data.get('password') == hashed_password:
                    logger.info("Contraseña correcta")
                    
                    # Crear o obtener usuario de Django
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
                        logger.info("Usuario de Django creado")
                    
                    # Actualizar último acceso en MongoDB
                    users_collection.update_one(
                        {'_id': user_data['_id']},
                        {'$set': {'last_login': datetime.now().isoformat()}}
                    )
                    
                    return user
                else:
                    logger.warning("Contraseña incorrecta")
            else:
                logger.warning(f"Usuario no encontrado: {username}")
                
        except Exception as e:
            logger.error(f"Error en autenticación: {str(e)}")
            return None
        
        return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
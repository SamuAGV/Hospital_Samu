# apps/users/backends.py
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from django.conf import settings
import hashlib
from datetime import datetime
import logging
import os

logger = logging.getLogger(__name__)

class MongoDBBackend(BaseBackend):
    """
    Backend de autenticación que usa MongoDB directamente.
    """
    
    def authenticate(self, request, username=None, password=None):
        # Log 1: Verificar que se llama al backend
        logger.info("=" * 50)
        logger.info(f"Intento de autenticación para: {username}")
        logger.info(f"MONGO_CONNECTED: {settings.MONGO_CONNECTED}")
        logger.info(f"MONGO_DB is None: {settings.MONGO_DB is None}")
        
        # Verificar conexión a MongoDB
        if not settings.MONGO_CONNECTED or settings.MONGO_DB is None:
            logger.error("MongoDB NO está conectado")
            logger.error(f"MONGO_URI: {settings.MONGO_URI[:50]}...")  # Solo los primeros 50 caracteres
            logger.error(f"MONGO_DB_NAME: {settings.MONGO_DB_NAME}")
            logger.error(f"Variables de entorno en Vercel: {list(os.environ.keys())}")
            return None
        
        try:
            db = settings.MONGO_DB
            users_collection = db['users']
            
            # Log 2: Buscar usuario
            logger.info(f"Buscando usuario: {username}")
            user_data = users_collection.find_one({
                '$or': [
                    {'username': username},
                    {'email': username}
                ]
            })
            
            if not user_data:
                logger.warning(f"Usuario no encontrado: {username}")
                # Listar usuarios existentes para depuración
                all_users = list(users_collection.find({}, {'username': 1, 'email': 1}))
                logger.info(f"Usuarios en BD: {[u.get('username') for u in all_users]}")
                return None
            
            logger.info(f"Usuario encontrado: {user_data.get('username')}")
            logger.info(f"Email: {user_data.get('email')}")
            
            # Verificar contraseña
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            stored_password = user_data.get('password')
            
            logger.info(f"Contraseña hasheada en BD: {stored_password[:20]}...")
            logger.info(f"Contraseña ingresada hasheada: {hashed_password[:20]}...")
            
            if stored_password == hashed_password:
                logger.info("Contraseña correcta")
                
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
                
                logger.info("Autenticación exitosa")
                return user
            else:
                logger.warning("Contraseña incorrecta")
                return None
                
        except Exception as e:
            logger.error(f"💥 Error en autenticación: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
# apps/users/backends.py
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from django.conf import settings
from .utils import verify_password
import logging
import sys

logger = logging.getLogger(__name__)

class MongoDBBackend(BaseBackend):
    
    def authenticate(self, request, username=None, password=None):
        # Logs para ver en Vercel
        print(f"Autenticando: {username}", file=sys.stderr)
        logger.info(f"Autenticando: {username}")
        
        if not settings.MONGO_CONNECTED or settings.MONGO_DB is None:
            print("MongoDB no conectado", file=sys.stderr)
            logger.error("MongoDB no conectado")
            return None
        
        try:
            db = settings.MONGO_DB
            users_collection = db['users']
            
            # Buscar usuario
            print(f"Buscando en MongoDB: {username}", file=sys.stderr)
            user_data = users_collection.find_one({
                '$or': [{'username': username}, {'email': username}]
            })
            
            if not user_data:
                print(f"Usuario no encontrado: {username}", file=sys.stderr)
                logger.warning(f"Usuario no encontrado: {username}")
                return None
            
            print(f"Usuario encontrado en MongoDB: {user_data.get('username')}", file=sys.stderr)
            
            # Verificar contraseña
            stored_password = user_data.get('password', '')
            if not verify_password(password, stored_password):
                print(f"Contraseña incorrecta para: {username}", file=sys.stderr)
                logger.warning(f"Contraseña incorrecta para: {username}")
                return None
            
            print(f"Contraseña verificada para: {username}", file=sys.stderr)
            
            # Crear o obtener usuario de Django
            try:
                print(f"Buscando usuario en Django: {username}", file=sys.stderr)
                user = User.objects.get(username=user_data['username'])
                print(f"Usuario Django encontrado: {user.username}", file=sys.stderr)
                
                # Actualizar campos si es necesario
                updated = False
                if user.email != user_data.get('email', ''):
                    user.email = user_data.get('email', '')
                    updated = True
                if user.first_name != user_data.get('first_name', ''):
                    user.first_name = user_data.get('first_name', '')
                    updated = True
                if user.last_name != user_data.get('last_name', ''):
                    user.last_name = user_data.get('last_name', '')
                    updated = True
                if user.is_staff != user_data.get('is_staff', False):
                    user.is_staff = user_data.get('is_staff', False)
                    updated = True
                if user.is_superuser != user_data.get('is_superuser', False):
                    user.is_superuser = user_data.get('is_superuser', False)
                    updated = True
                
                if updated:
                    user.save()
                    print(f"Usuario Django actualizado: {user.username}", file=sys.stderr)
                    
            except User.DoesNotExist:
                print(f"Creando usuario Django: {user_data['username']}", file=sys.stderr)
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
                print(f"Usuario Django creado: {user.username}", file=sys.stderr)
            
            # Actualizar último acceso en MongoDB
            users_collection.update_one(
                {'_id': user_data['_id']},
                {'$set': {'last_login': datetime.now().isoformat()}}
            )
            
            print(f"Autenticación exitosa para: {user.username}", file=sys.stderr)
            logger.info(f"Autenticación exitosa para: {user.username}")
            return user
            
        except Exception as e:
            print(f"Error: {str(e)}", file=sys.stderr)
            import traceback
            print(traceback.format_exc(), file=sys.stderr)
            logger.error(f"Error: {str(e)}")
            return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
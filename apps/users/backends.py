# apps/users/backends.py
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from django.conf import settings
from .utils import hash_password, verify_password
from datetime import datetime
import logging
import sys

logger = logging.getLogger(__name__)

class MongoDBBackend(BaseBackend):
    """
    Backend de autenticación que usa MongoDB directamente.
    """
    
    def authenticate(self, request, username=None, password=None):
        print("=" * 60, file=sys.stderr)
        print(f"AUTHENTICATE CALLED for: {username}", file=sys.stderr)
        
        if not settings.MONGO_CONNECTED or settings.MONGO_DB is None:
            print("MongoDB NO está conectado", file=sys.stderr)
            return None
        
        try:
            db = settings.MONGO_DB
            users_collection = db['users']
            
            # Buscar usuario
            user_data = users_collection.find_one({
                '$or': [
                    {'username': username},
                    {'email': username}
                ]
            })
            
            if not user_data:
                print(f"Usuario no encontrado: {username}", file=sys.stderr)
                return None
            
            print(f"Usuario encontrado: {user_data.get('username')}", file=sys.stderr)
            
            # Verificar contraseña
            stored_password = user_data.get('password', '')
            
            if not verify_password(password, stored_password):
                print(f"Contraseña incorrecta para: {username}", file=sys.stderr)
                return None
            
            print("Contraseña válida", file=sys.stderr)
            
            # Crear o obtener usuario de Django
            try:
                print(f"Buscando usuario de Django: {user_data['username']}", file=sys.stderr)
                user = User.objects.get(username=user_data['username'])
                print(f"Usuario de Django encontrado: {user.username}", file=sys.stderr)
                
                # Actualizar datos del usuario de Django
                if user.email != user_data.get('email', ''):
                    user.email = user_data.get('email', '')
                    user.save()
                    print(f"Email actualizado: {user.email}", file=sys.stderr)
                    
            except User.DoesNotExist:
                print(f"Creando nuevo usuario de Django: {user_data['username']}", file=sys.stderr)
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
                print(f"Usuario de Django creado: {user.username}", file=sys.stderr)
            
            # Actualizar último acceso en MongoDB
            users_collection.update_one(
                {'_id': user_data['_id']},
                {'$set': {'last_login': datetime.now().isoformat()}}
            )
            
            print(f"Autenticación exitosa para: {user.username}", file=sys.stderr)
            return user
                
        except Exception as e:
            print(f"Error en autenticación: {str(e)}", file=sys.stderr)
            import traceback
            print(traceback.format_exc(), file=sys.stderr)
            return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
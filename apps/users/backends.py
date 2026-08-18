# apps/users/backends.py
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from django.conf import settings
from django.db import connection
from django.core.management import call_command
from .utils import verify_password
import logging
import sys
import os

logger = logging.getLogger(__name__)

class MongoDBBackend(BaseBackend):
    
    def ensure_django_tables(self):
        """Asegura que las tablas de Django existen ejecutando migraciones."""
        try:
            # Verificar si la tabla auth_user existe
            with connection.cursor() as cursor:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='auth_user'")
                table_exists = cursor.fetchone()
            
            if table_exists:
                print("✅ Tablas de Django ya existen", file=sys.stderr)
                return True
            
            print("📦 Tablas de Django no encontradas. Ejecutando migraciones...", file=sys.stderr)
            
            # Ejecutar migraciones
            call_command('migrate', interactive=False, verbosity=1)
            
            # Verificar nuevamente
            with connection.cursor() as cursor:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='auth_user'")
                if cursor.fetchone():
                    print("✅ Migraciones ejecutadas exitosamente", file=sys.stderr)
                    return True
                else:
                    print("❌ Las migraciones no crearon la tabla auth_user", file=sys.stderr)
                    return False
            
        except Exception as e:
            print(f"⚠️ Error al crear tablas: {e}", file=sys.stderr)
            import traceback
            print(traceback.format_exc(), file=sys.stderr)
            return False
    
    def authenticate(self, request, username=None, password=None):
        print(f"🔐 Autenticando: {username}", file=sys.stderr)
        
        # Asegurar que las tablas de Django existen
        if not self.ensure_django_tables():
            print("❌ No se pudieron crear las tablas de Django", file=sys.stderr)
            return None
        
        if not settings.MONGO_CONNECTED or settings.MONGO_DB is None:
            print("❌ MongoDB no conectado", file=sys.stderr)
            return None
        
        try:
            db = settings.MONGO_DB
            users_collection = db['users']
            
            # Buscar usuario
            user_data = users_collection.find_one({
                '$or': [{'username': username}, {'email': username}]
            })
            
            if not user_data:
                print(f"❌ Usuario no encontrado: {username}", file=sys.stderr)
                return None
            
            print(f"✅ Usuario encontrado en MongoDB: {user_data.get('username')}", file=sys.stderr)
            
            # Verificar contraseña
            stored_password = user_data.get('password', '')
            if not verify_password(password, stored_password):
                print(f"❌ Contraseña incorrecta para: {username}", file=sys.stderr)
                return None
            
            print(f"✅ Contraseña verificada para: {username}", file=sys.stderr)
            
            # Crear o obtener usuario de Django
            try:
                user = User.objects.get(username=user_data['username'])
                print(f"✅ Usuario Django encontrado: {user.username}", file=sys.stderr)
            except User.DoesNotExist:
                print(f"🆕 Creando usuario Django: {user_data['username']}", file=sys.stderr)
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
                print(f"✅ Usuario Django creado: {user.username}", file=sys.stderr)
            
            print(f"🎉 Autenticación exitosa para: {user.username}", file=sys.stderr)
            return user
            
        except Exception as e:
            print(f"💥 Error en autenticación: {str(e)}", file=sys.stderr)
            import traceback
            print(traceback.format_exc(), file=sys.stderr)
            return None
    
    def get_user(self, user_id):
        self.ensure_django_tables()
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
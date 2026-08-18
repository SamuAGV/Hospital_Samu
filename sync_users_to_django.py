# sync_users_to_django.py
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_project.settings')

django.setup()

from django.contrib.auth.models import User
from django.conf import settings
from apps.users.utils import hash_password
import pymongo
import certifi

def sync_users():
    print("=" * 60)
    print("SINCRONIZANDO USUARIOS DE MONGODB A DJANGO")
    print("=" * 60)
    
    if not settings.MONGO_CONNECTED or settings.MONGO_DB is None:
        print("❌ MongoDB no está conectado")
        return
    
    try:
        db = settings.MONGO_DB
        users_collection = db['users']
        
        # Obtener todos los usuarios de MongoDB
        mongo_users = list(users_collection.find({}))
        print(f"📋 Encontrados {len(mongo_users)} usuarios en MongoDB")
        
        created = 0
        updated = 0
        
        for mongo_user in mongo_users:
            username = mongo_user.get('username')
            
            # Verificar si existe en Django
            user, created_flag = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': mongo_user.get('email', ''),
                    'first_name': mongo_user.get('first_name', ''),
                    'last_name': mongo_user.get('last_name', ''),
                    'is_active': mongo_user.get('is_active', True),
                    'is_staff': mongo_user.get('is_staff', False),
                    'is_superuser': mongo_user.get('is_superuser', False),
                }
            )
            
            if created_flag:
                user.set_unusable_password()
                user.save()
                created += 1
                print(f"✅ Creado: {username}")
            else:
                # Actualizar si es necesario
                updated_flag = False
                if user.email != mongo_user.get('email', ''):
                    user.email = mongo_user.get('email', '')
                    updated_flag = True
                if user.first_name != mongo_user.get('first_name', ''):
                    user.first_name = mongo_user.get('first_name', '')
                    updated_flag = True
                if user.last_name != mongo_user.get('last_name', ''):
                    user.last_name = mongo_user.get('last_name', '')
                    updated_flag = True
                
                if updated_flag:
                    user.save()
                    updated += 1
                    print(f"🔄 Actualizado: {username}")
                else:
                    print(f"ℹ️  Sin cambios: {username}")
        
        print("\n" + "=" * 60)
        print(f"📊 Resumen: {created} creados, {updated} actualizados")
        
        # Listar todos los usuarios de Django
        print("\n" + "=" * 60)
        print("USUARIOS EN DJANGO:")
        for user in User.objects.all():
            print(f"  - {user.username} ({user.email}) - Staff: {user.is_staff}, Superuser: {user.is_superuser}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    sync_users()
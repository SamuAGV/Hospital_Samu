# apps/users/management/commands/sync_users.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.conf import settings
import pymongo
import certifi

class Command(BaseCommand):
    help = 'Sincroniza usuarios de MongoDB a Django'

    def handle(self, *args, **options):
        self.stdout.write('🔄 Sincronizando usuarios de MongoDB a Django...')
        
        if not settings.MONGO_CONNECTED or settings.MONGO_DB is None:
            self.stdout.write(self.style.ERROR('❌ MongoDB no está conectado'))
            return
        
        db = settings.MONGO_DB
        users_collection = db['users']
        
        # Obtener todos los usuarios de MongoDB
        mongo_users = list(users_collection.find({}))
        self.stdout.write(f'📋 Encontrados {len(mongo_users)} usuarios en MongoDB')
        
        created = 0
        updated = 0
        
        for mongo_user in mongo_users:
            username = mongo_user.get('username')
            if not username:
                continue
            
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
                self.stdout.write(f'✅ Creado: {username}')
            else:
                # Actualizar campos si es necesario
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
                if user.is_staff != mongo_user.get('is_staff', False):
                    user.is_staff = mongo_user.get('is_staff', False)
                    updated_flag = True
                if user.is_superuser != mongo_user.get('is_superuser', False):
                    user.is_superuser = mongo_user.get('is_superuser', False)
                    updated_flag = True
                
                if updated_flag:
                    user.save()
                    updated += 1
                    self.stdout.write(f'🔄 Actualizado: {username}')
                else:
                    self.stdout.write(f'ℹ️ Sin cambios: {username}')
        
        self.stdout.write(self.style.SUCCESS(
            f'✅ Sincronización completada: {created} creados, {updated} actualizados'
        ))
        self.stdout.write(f'📊 Total usuarios en Django: {User.objects.count()}')
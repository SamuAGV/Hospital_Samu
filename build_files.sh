#!/bin/bash
# build_files.sh

echo "Iniciando build de Vercel..."

# Instalar dependencias
echo "Instalando dependencias..."
pip install -r requirements.txt

# Ejecutar migraciones forzadas
echo "Ejecutando migraciones..."
python -c "
import os
import sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_project.settings')
sys.path.append(os.getcwd())

import django
django.setup()

from django.core.management import call_command
from django.db import connection

print('Verificando tablas...')
with connection.cursor() as cursor:
    cursor.execute('SELECT name FROM sqlite_master WHERE type=\"table\" AND name=\"auth_user\"')
    exists = cursor.fetchone()
    
if not exists:
    print('Ejecutando migraciones...')
    call_command('migrate', interactive=False, verbosity=1)
    print('Migraciones completadas')
else:
    print('Las tablas ya existen')
"

# Sincronizar usuarios
echo "Sincronizando usuarios..."
python -c "
import os
import sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_project.settings')
sys.path.append(os.getcwd())

import django
django.setup()

from django.contrib.auth.models import User
from django.conf import settings
import pymongo
import certifi

print('Conectando a MongoDB...')
if settings.MONGO_URI:
    try:
        client = pymongo.MongoClient(settings.MONGO_URI, tlsCAFile=certifi.where())
        db = client[settings.MONGO_DB_NAME]
        users_collection = db['users']
        
        users = list(users_collection.find({}))
        print(f'Encontrados {len(users)} usuarios en MongoDB')
        
        created_count = 0
        for user_data in users:
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
                    created_count += 1
                    print(f'Usuario creado: {username}')
        print(f'{created_count} usuarios creados, total: {User.objects.count()}')
        client.close()
    except Exception as e:
        print(f'Error sincronizando: {e}')
"

echo "Build completado!"
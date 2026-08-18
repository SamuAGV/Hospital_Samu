#!/bin/bash
# build_files.sh

echo "🚀 Iniciando build de Vercel..."

# Ejecutar migraciones
echo "📦 Ejecutando migraciones..."
python manage.py makemigrations
python manage.py migrate

# Sincronizar usuarios de MongoDB a Django
echo "🔄 Sincronizando usuarios..."
python manage.py shell -c "
from django.contrib.auth.models import User
from django.conf import settings
import pymongo
import certifi

if settings.MONGO_CONNECTED and settings.MONGO_DB is not None:
    db = settings.MONGO_DB
    users_collection = db['users']
    users = list(users_collection.find({}))
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
                print(f'✅ Usuario creado: {username}')
            else:
                print(f'ℹ️ Usuario existente: {username}')
    print(f'📊 Total usuarios en Django: {User.objects.count()}')
else:
    print('❌ MongoDB no conectado, no se pueden sincronizar usuarios')
"

echo "✅ Build completado!"
"""
Script para crear un usuario administrador en Django
Ejecutar: python manage.py shell < create_admin.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_project.settings')
django.setup()

from django.contrib.auth.models import User

def create_admin():
    """Crear usuario administrador si no existe."""
    username = 'admin'
    email = 'admin@hospital.com'
    password = 'admin123'
    
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username, email, password)
        print(f"✅ Usuario administrador creado: {username} / {password}")
    else:
        print(f"ℹ️ Usuario administrador ya existe: {username}")

if __name__ == "__main__":
    create_admin()
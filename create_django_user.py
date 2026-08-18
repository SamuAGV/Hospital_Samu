# create_django_user.py
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_project.settings')

django.setup()

from django.contrib.auth.models import User
from django.conf import settings
from apps.users.utils import hash_password

def create_django_user():
    print("=" * 50)
    print("CREANDO USUARIO EN DJANGO")
    print("=" * 50)
    
    try:
        # Verificar si el usuario ya existe en Django
        if User.objects.filter(username='admin').exists():
            print("✅ Usuario admin ya existe en Django")
            user = User.objects.get(username='admin')
            print(f"   Username: {user.username}")
            print(f"   Email: {user.email}")
            print(f"   Is active: {user.is_active}")
            print(f"   Is staff: {user.is_staff}")
            print(f"   Is superuser: {user.is_superuser}")
        else:
            print("🆕 Creando usuario admin en Django...")
            user = User(
                username='admin',
                email='admin@medinsight.com',
                first_name='Administrador',
                last_name='Sistema',
                is_active=True,
                is_staff=True,
                is_superuser=True,
            )
            user.set_unusable_password()
            user.save()
            print("✅ Usuario admin creado en Django")
        
        # Listar todos los usuarios de Django
        print("\n" + "=" * 50)
        print("USUARIOS EN DJANGO:")
        for u in User.objects.all():
            print(f"  - {u.username} ({u.email}) - Staff: {u.is_staff}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    create_django_user()
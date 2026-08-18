# run_migrations.py
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_project.settings')

django.setup()

from django.core.management import call_command
from django.db import connection

def run_migrations():
    print("📦 Ejecutando migraciones...")
    try:
        # Verificar si la tabla auth_user existe
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='auth_user'")
            table_exists = cursor.fetchone()
        
        if not table_exists:
            call_command('migrate', interactive=False, verbosity=1)
            print("✅ Migraciones ejecutadas")
        else:
            print("ℹ️ Las tablas ya existen")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    run_migrations()
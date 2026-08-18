import os
import sys
import pymongo
import certifi
import hashlib
from datetime import datetime

# Configuración
MONGO_URI = "mongodb+srv://Samu:mongodb@cluster0.gtzyuap.mongodb.net/"
MONGO_DB_NAME = "medinsight_hospital"

def test_connection():
    try:
        print("Conectando a MongoDB...")
        client = pymongo.MongoClient(MONGO_URI, tlsCAFile=certifi.where())
        db = client[MONGO_DB_NAME]
        
        # Probar conexión
        client.admin.command('ping')
        print("✅ Conexión exitosa!")
        
        # Obtener colección de usuarios
        users_collection = db['users']
        
        # Crear índices
        users_collection.create_index('username', unique=True)
        users_collection.create_index('email', unique=True)
        print("✅ Índices creados")
        
        # Verificar si existe usuario admin
        admin = users_collection.find_one({'username': 'admin'})
        if admin:
            print(f"✅ Usuario admin ya existe: {admin['email']}")
        else:
            # Crear usuario admin
            admin_data = {
                'username': 'admin',
                'email': 'admin@medinsight.com',
                'password': hashlib.sha256('admin123'.encode()).hexdigest(),
                'first_name': 'Administrador',
                'last_name': 'Sistema',
                'is_active': True,
                'is_staff': True,
                'is_superuser': True,
                'date_joined': datetime.now().isoformat(),
                'last_login': None,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
            }
            result = users_collection.insert_one(admin_data)
            print("✅ Usuario admin creado!")
            print(f"   Usuario: admin")
            print(f"   Contraseña: admin123")
        
        # Listar todos los usuarios
        print("\n📋 Usuarios registrados:")
        for user in users_collection.find({}, {'username': 1, 'email': 1, 'is_superuser': 1}):
            admin_tag = " (Admin)" if user.get('is_superuser') else ""
            print(f"  - {user['username']} <{user['email']}>{admin_tag}")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    test_connection()
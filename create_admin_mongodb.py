import os
import sys
import hashlib
from datetime import datetime
import pymongo
import certifi

# Configuración
MONGO_URI = "mongodb+srv://Samu:mongodb@cluster0.gtzyuap.mongodb.net/"
MONGO_DB_NAME = "medinsight_hospital"

def create_admin_user():
    try:
        # Conectar a MongoDB
        client = pymongo.MongoClient(MONGO_URI, tlsCAFile=certifi.where())
        db = client[MONGO_DB_NAME]
        users_collection = db['users']
        
        # Crear índices
        users_collection.create_index('username', unique=True)
        users_collection.create_index('email', unique=True)
        
        # Datos del admin
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
        
        # Verificar si ya existe
        existing = users_collection.find_one({'username': 'admin'})
        if existing:
            print("El usuario admin ya existe en MongoDB")
            print(f"ID: {existing['_id']}")
            print(f"Email: {existing['email']}")
        else:
            result = users_collection.insert_one(admin_data)
            print("Usuario admin creado exitosamente!")
            print(f"ID: {result.inserted_id}")
            print("Usuario: admin")
            print("Contraseña: admin123")
        
        # Listar todos los usuarios
        print("\nUsuarios registrados:")
        for user in users_collection.find({}, {'username': 1, 'email': 1, 'is_superuser': 1}):
            print(f"  - {user['username']} ({user['email']}) {'(Admin)' if user.get('is_superuser') else ''}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    create_admin_user()
import os
import sys
import pymongo
import certifi
from datetime import datetime

# Configuración
MONGO_URI = "mongodb+srv://Samu:mongodb@cluster0.gtzyuap.mongodb.net/"
MONGO_DB_NAME = "medinsight_hospital"

def check_users():
    try:
        # Conectar a MongoDB
        client = pymongo.MongoClient(MONGO_URI, tlsCAFile=certifi.where())
        db = client[MONGO_DB_NAME]
        users_collection = db['users']
        
        print("=" * 50)
        print("USUARIOS REGISTRADOS EN MONGODB")
        print("=" * 50)
        
        # Contar usuarios
        total = users_collection.count_documents({})
        print(f"Total de usuarios: {total}\n")
        
        # Listar todos los usuarios
        for user in users_collection.find({}):
            print(f"Usuario: {user.get('username')}")
            print(f"  Email: {user.get('email')}")
            print(f"  Nombre: {user.get('first_name', '')} {user.get('last_name', '')}")
            print(f"  Admin: {'Sí' if user.get('is_superuser') else 'No'}")
            print(f"  Activo: {'Sí' if user.get('is_active') else 'No'}")
            print(f"  Registrado: {user.get('date_joined', '')[:19]}")
            print("-" * 30)
        
        client.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    check_users()
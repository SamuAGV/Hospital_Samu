# fix_passwords.py
import os
import sys
import pymongo
import certifi
import hashlib

# Configuración
MONGO_URI = "mongodb+srv://Samu:mongodb@cluster0.gtzyuap.mongodb.net/"
MONGO_DB_NAME = "medinsight_hospital"

def hash_password(password):
    """Hashea una contraseña de manera consistente."""
    if isinstance(password, str):
        return hashlib.sha256(password.encode('utf-8')).hexdigest()
    return hashlib.sha256(password).hexdigest()

def fix_passwords():
    try:
        print("Conectando a MongoDB...")
        client = pymongo.MongoClient(MONGO_URI, tlsCAFile=certifi.where())
        db = client[MONGO_DB_NAME]
        users_collection = db['users']
        
        print("=" * 50)
        print("ACTUALIZANDO CONTRASEÑAS")
        print("=" * 50)
        
        # Obtener todos los usuarios
        users = list(users_collection.find({}))
        
        for user in users:
            username = user.get('username')
            current_password = user.get('password', '')
            
            print(f"\nUsuario: {username}")
            print(f"Contraseña actual: {current_password[:20]}...")
            
            # Si la contraseña parece ser plana (no hasheada), hashearla
            if len(current_password) != 64:  # SHA256 produce 64 caracteres hexadecimales
                print(f"⚠️ Contraseña no hasheada para {username}")
                
                # Preguntar la nueva contraseña
                new_password = input(f"Ingresa nueva contraseña para {username}: ")
                
                if new_password:
                    new_hash = hash_password(new_password)
                    users_collection.update_one(
                        {'_id': user['_id']},
                        {'$set': {'password': new_hash}}
                    )
                    print(f"✅ Contraseña actualizada para {username}")
                else:
                    print(f"❌ No se actualizó la contraseña para {username}")
            else:
                print(f"✅ Contraseña ya hasheada para {username}")
        
        print("\n" + "=" * 50)
        print("VERIFICANDO USUARIOS ACTUALIZADOS")
        print("=" * 50)
        
        for user in users_collection.find({}, {'username': 1, 'password': 1}):
            print(f"Usuario: {user['username']}")
            print(f"  Hash: {user['password'][:20]}...")
            print(f"  Longitud: {len(user['password'])}")
        
        client.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    fix_passwords()
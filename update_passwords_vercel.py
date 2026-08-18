# update_passwords_vercel.py
import os
import sys
import pymongo
import certifi
import hashlib
from datetime import datetime

# Configuración - USA LA MISMA URI QUE TIENES EN VERCEL
MONGO_URI = "mongodb+srv://Samu:mongodb@cluster0.gtzyuap.mongodb.net/"
MONGO_DB_NAME = "medinsight_hospital"

def hash_password(password):
    """Hashea una contraseña de manera consistente."""
    if isinstance(password, str):
        return hashlib.sha256(password.encode('utf-8')).hexdigest()
    return hashlib.sha256(password).hexdigest()

def update_passwords():
    try:
        print("🔌 Conectando a MongoDB...")
        client = pymongo.MongoClient(MONGO_URI, tlsCAFile=certifi.where())
        db = client[MONGO_DB_NAME]
        users_collection = db['users']
        
        print("=" * 60)
        print("ACTUALIZANDO CONTRASEÑAS PARA VERCEL")
        print("=" * 60)
        
        # Obtener todos los usuarios
        users = list(users_collection.find({}))
        
        print(f"\n📋 Encontrados {len(users)} usuarios:\n")
        
        for i, user in enumerate(users, 1):
            username = user.get('username')
            current_password = user.get('password', '')
            email = user.get('email', '')
            
            print(f"{i}. Usuario: {username} ({email})")
            print(f"   Hash actual: {current_password[:20]}...")
            print(f"   Longitud del hash: {len(current_password)}")
            
            # Preguntar la nueva contraseña
            print(f"\n   🔑 Ingresa la nueva contraseña para '{username}'")
            print(f"   (Presiona Enter para mantener la contraseña actual)")
            new_password = input("   Nueva contraseña: ").strip()
            
            if new_password:
                # Hashear la nueva contraseña
                new_hash = hash_password(new_password)
                
                # Actualizar en MongoDB
                result = users_collection.update_one(
                    {'_id': user['_id']},
                    {'$set': {
                        'password': new_hash,
                        'updated_at': datetime.now().isoformat()
                    }}
                )
                
                if result.modified_count > 0:
                    print(f"   ✅ Contraseña actualizada para '{username}'\n")
                else:
                    print(f"   ❌ Error al actualizar para '{username}'\n")
            else:
                print(f"   ⏭️  Manteniendo contraseña actual para '{username}'\n")
        
        print("=" * 60)
        print("VERIFICANDO USUARIOS ACTUALIZADOS")
        print("=" * 60)
        
        for user in users_collection.find({}, {'username': 1, 'email': 1, 'password': 1}):
            username = user.get('username')
            email = user.get('email')
            password_hash = user.get('password', '')
            
            print(f"\n👤 Usuario: {username}")
            print(f"   📧 Email: {email}")
            print(f"   🔑 Hash: {password_hash[:30]}...")
            print(f"   📏 Longitud: {len(password_hash)}")
            
            # Verificar si el hash tiene la longitud correcta (64 para SHA256)
            if len(password_hash) == 64:
                print(f"   ✅ Hash válido (SHA256)")
            else:
                print(f"   ⚠️  Hash con longitud inusual: {len(password_hash)}")
        
        client.close()
        print("\n✅ Proceso completado!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    update_passwords()
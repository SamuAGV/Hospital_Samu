# fix_passwords_vercel.py
import pymongo
import certifi
import hashlib

MONGO_URI = "mongodb+srv://Samu:mongodb@cluster0.gtzyuap.mongodb.net/"
MONGO_DB_NAME = "medinsight_hospital"

def hash_password(password):
    """Hashea una contraseña de manera consistente."""
    if isinstance(password, str):
        return hashlib.sha256(password.encode('utf-8')).hexdigest()
    return hashlib.sha256(password).hexdigest()

def fix_passwords():
    try:
        print("🔌 Conectando a MongoDB...")
        client = pymongo.MongoClient(MONGO_URI, tlsCAFile=certifi.where())
        db = client[MONGO_DB_NAME]
        users_collection = db['users']
        
        print("=" * 60)
        print("ACTUALIZANDO CONTRASEÑAS PARA VERCEL")
        print("=" * 60)
        
        # Contraseñas que funcionarán en Vercel
        users_to_update = [
            {'username': 'admin', 'password': 'admin123'},
            {'username': 'Samuel', 'password': '654321'},
            {'username': 'Ana', 'password': 'ana123'},
        ]
        
        for user_data in users_to_update:
            username = user_data['username']
            password = user_data['password']
            
            # Generar el hash que funcionará en Vercel
            new_hash = hash_password(password)
            
            # Actualizar en MongoDB
            result = users_collection.update_one(
                {'username': username},
                {'$set': {'password': new_hash}}
            )
            
            if result.modified_count > 0:
                print(f"✅ {username}: Contraseña actualizada")
                print(f"   Nuevo hash: {new_hash[:30]}...")
            elif result.matched_count > 0:
                print(f"ℹ️  {username}: Ya tiene la contraseña correcta")
            else:
                print(f"❌ {username}: No encontrado")
        
        # Verificar los usuarios actualizados
        print("\n" + "=" * 60)
        print("VERIFICACIÓN FINAL")
        print("=" * 60)
        
        for user in users_collection.find({}, {'username': 1, 'password': 1}):
            username = user.get('username')
            password_hash = user.get('password', '')
            
            # Verificar si el hash es correcto para admin123
            if username == 'admin':
                test_hash = hash_password('admin123')
                is_correct = test_hash == password_hash
                print(f"{'✅' if is_correct else '❌'} admin: {is_correct}")
            
            print(f"   {username}: {password_hash[:30]}...")
        
        client.close()
        print("\n✅ Proceso completado!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    fix_passwords()
    
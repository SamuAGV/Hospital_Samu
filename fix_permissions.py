# fix_permissions.py
import pymongo
import certifi

MONGO_URI = "mongodb+srv://Samu:mongodb@cluster0.gtzyuap.mongodb.net/"
MONGO_DB_NAME = "medinsight_hospital"

def fix_permissions():
    try:
        print("🔌 Conectando a MongoDB...")
        client = pymongo.MongoClient(MONGO_URI, tlsCAFile=certifi.where())
        db = client[MONGO_DB_NAME]
        users_collection = db['users']
        
        # Actualizar permisos de admin
        result = users_collection.update_one(
            {'username': 'admin'},
            {'$set': {
                'is_staff': True,
                'is_superuser': True,
                'is_active': True
            }}
        )
        
        if result.modified_count > 0:
            print("✅ Permisos de admin actualizados")
        else:
            print("ℹ️ Admin ya tiene los permisos correctos")
        
        # Actualizar permisos de Samuel
        result = users_collection.update_one(
            {'username': 'Samuel'},
            {'$set': {
                'is_staff': True,
                'is_superuser': False,
                'is_active': True
            }}
        )
        
        if result.modified_count > 0:
            print("✅ Permisos de Samuel actualizados")
        else:
            print("ℹ️ Samuel ya tiene los permisos correctos")
        
        # Verificar todos los usuarios
        print("\n📋 Usuarios en MongoDB:")
        for user in users_collection.find({}, {'username': 1, 'is_staff': 1, 'is_superuser': 1}):
            print(f"  - {user['username']}: Staff={user.get('is_staff', False)}, Superuser={user.get('is_superuser', False)}")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    fix_permissions()
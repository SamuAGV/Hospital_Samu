"""
Script para verificar la conexión a MongoDB con certificados SSL
Ejecutar: python check_mongodb.py
"""

import os
import sys
import certifi
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

def check_mongodb():
    """Verificar conexión a MongoDB con manejo de SSL."""
    MONGO_URI = os.getenv('MONGO_URI')
    MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', 'medinsight_hospital')
    
    print("=" * 60)
    print("🔍 VERIFICANDO CONEXIÓN A MONGODB")
    print("=" * 60)
    print(f"URI: {MONGO_URI[:40]}...")
    print(f"Base de datos: {MONGO_DB_NAME}")
    print()
    
    try:
        # Usar certifi para el certificado SSL
        client = MongoClient(
            MONGO_URI,
            tlsCAFile=certifi.where(),
            serverSelectionTimeoutMS=10000
        )
        
        db = client[MONGO_DB_NAME]
        
        # Probar conexión
        client.admin.command('ping')
        print("✅ Conexión exitosa a MongoDB")
        
        # Mostrar colecciones
        collections = db.list_collection_names()
        print(f"\n📁 Colecciones en {MONGO_DB_NAME}:")
        if collections:
            for coll in collections:
                count = db[coll].count_documents({})
                print(f"  - {coll}: {count} documentos")
        else:
            print("  (No hay colecciones creadas)")
        
        print("\n✅ Verificación completada")
        return True
        
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        print("\nVerifica que:")
        print("  1. La URI en .env sea correcta")
        print("  2. Tengas conexión a Internet")
        print("  3. El usuario y contraseña sean correctos")
        print("  4. Certifi esté instalado: pip install certifi")
        return False

if __name__ == "__main__":
    check_mongodb()
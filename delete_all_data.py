"""
Script para ELIMINAR TODOS LOS DATOS de MongoDB
Ejecutar: python delete_all_data.py
"""

import os
import sys
import certifi
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv('MONGO_URI')
MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', 'medinsight_hospital')

def get_mongo_connection():
    try:
        client = MongoClient(
            MONGO_URI,
            tlsCAFile=certifi.where(),
            serverSelectionTimeoutMS=10000
        )
        db = client[MONGO_DB_NAME]
        client.admin.command('ping')
        print(f"✅ Conectado a MongoDB: {MONGO_DB_NAME}")
        return db
    except Exception as e:
        print(f"❌ Error conectando a MongoDB: {e}")
        sys.exit(1)

def delete_all_data(db):
    """Eliminar TODOS los datos de todas las colecciones."""
    
    print("\n" + "="*60)
    print("⚠️  ELIMINANDO TODOS LOS DATOS DE MONGODB")
    print("="*60)
    
    # Mostrar datos actuales
    print("\n📊 DATOS ACTUALES:")
    collections = db.list_collection_names()
    total = 0
    for coll in collections:
        count = db[coll].count_documents({})
        print(f"  - {coll}: {count:,} documentos")
        total += count
    
    print(f"\n📝 TOTAL: {total:,} documentos")
    
    # Confirmar
    print("\n⚠️  ¿Estás seguro de que quieres ELIMINAR TODOS los datos?")
    confirm = input("   Escribe 'SI' para confirmar: ")
    
    if confirm.upper() != 'SI':
        print("❌ Operación cancelada")
        return
    
    # Eliminar datos
    print("\n🗑️  Eliminando datos...")
    for coll in collections:
        result = db[coll].delete_many({})
        print(f"  - {coll}: {result.deleted_count} documentos eliminados")
    
    # Verificar
    print("\n📊 DESPUÉS DE ELIMINAR:")
    for coll in collections:
        count = db[coll].count_documents({})
        print(f"  - {coll}: {count} documentos")
    
    print("\n" + "="*60)
    print("✅ TODOS LOS DATOS ELIMINADOS")
    print("="*60)

if __name__ == "__main__":
    db = get_mongo_connection()
    delete_all_data(db)
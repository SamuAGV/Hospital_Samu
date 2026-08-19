"""
Script para insertar datos en colecciones vacías de MongoDB
Ejecutar: python insert_missing_data.py
"""

import os
import sys
import certifi
from datetime import datetime, timedelta
import random
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

def insert_emergencies(db, count=100):
    """Insertar datos de urgencias."""
    print(f"\n📝 Insertando {count} urgencias...")
    
    prioridades = ['Baja', 'Media', 'Alta', 'Crítica']
    estados = ['En espera', 'Atendido', 'Alta', 'Traslado']
    sintomas = [
        'Dolor de cabeza', 'Fiebre alta', 'Dolor abdominal', 
        'Dificultad respiratoria', 'Traumatismo', 'Dolor en el pecho',
        'Mareos', 'Náuseas', 'Convulsiones', 'Alergia grave'
    ]
    
    emergencies = []
    for i in range(count):
        fecha = datetime.now() - timedelta(
            days=random.randint(0, 30),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        emergencies.append({
            'id_paciente': random.randint(1, 1200),
            'fecha_hora_ingreso': fecha.isoformat(),
            'prioridad': random.choice(prioridades),
            'sintomas': random.choice(sintomas),
            'presion_arterial': f"{random.randint(100, 160)}/{random.randint(60, 100)}",
            'frecuencia_cardiaca': random.randint(60, 120),
            'temperatura': round(random.uniform(36.0, 39.5), 1),
            'notas': random.choice([
                'Paciente en observación',
                'Requiere atención inmediata',
                'Estable',
                'En espera de resultados'
            ]),
            'estado': random.choice(estados)
        })
    
    # Eliminar datos existentes y insertar nuevos
    db.emergencies.delete_many({})
    result = db.emergencies.insert_many(emergencies)
    print(f"✅ {len(result.inserted_ids)} urgencias insertadas")
    return len(result.inserted_ids)

def insert_lab_requests(db, count=150):
    """Insertar solicitudes de laboratorio."""
    print(f"\n📝 Insertando {count} solicitudes de laboratorio...")
    
    tipos_estudio = ['Laboratorio', 'Imagen', 'Patología', 'Genético']
    estados_lab = ['Solicitado', 'En Proceso', 'Completado', 'Cancelado']
    estudios = [
        'Hemograma completo', 'Química sanguínea', 'Radiografía de tórax',
        'Ultrasonido', 'Biopsia', 'PCR', 'Tomografía', 'Resonancia magnética',
        'Electrocardiograma', 'Espirometría', 'Prueba de esfuerzo', 'Ecocardiograma'
    ]
    
    lab_requests = []
    for i in range(count):
        fecha = datetime.now() - timedelta(days=random.randint(0, 30))
        lab_requests.append({
            'id_paciente': random.randint(1, 1200),
            'id_medico': random.randint(1, 50),
            'nombre_estudio': random.choice(estudios),
            'tipo_estudio': random.choice(tipos_estudio),
            'fecha_solicitud': fecha.isoformat(),
            'estado': random.choice(estados_lab),
            'observaciones': random.choice(['Urgente', 'Rutina', 'Control', 'Seguimiento']),
            'resultado': random.choice(['Normal', 'Anormal', 'Pendiente', 'No disponible']) if random.random() > 0.4 else None,
            'fecha_resultado': (fecha + timedelta(days=random.randint(1, 5))).isoformat() if random.random() > 0.4 else None
        })
    
    # Eliminar datos existentes y insertar nuevos
    db.lab_requests.delete_many({})
    result = db.lab_requests.insert_many(lab_requests)
    print(f"✅ {len(result.inserted_ids)} solicitudes de laboratorio insertadas")
    return len(result.inserted_ids)

def insert_medicines(db):
    """Insertar medicamentos."""
    print("\n📝 Insertando medicamentos...")
    
    medicamentos = [
        # Antipiréticos y analgésicos
        {'nombre': 'Paracetamol', 'principio_activo': 'Acetaminofén', 'presentacion': 'Tableta', 'concentracion': '500mg', 'precio_unitario': 15.50, 'stock': 100, 'stock_minimo': 20, 'requiere_receta': False},
        {'nombre': 'Ibuprofeno', 'principio_activo': 'Ibuprofeno', 'presentacion': 'Tableta', 'concentracion': '400mg', 'precio_unitario': 22.30, 'stock': 80, 'stock_minimo': 15, 'requiere_receta': False},
        {'nombre': 'Naproxeno', 'principio_activo': 'Naproxeno', 'presentacion': 'Tableta', 'concentracion': '250mg', 'precio_unitario': 28.00, 'stock': 60, 'stock_minimo': 10, 'requiere_receta': False},
        {'nombre': 'Diclofenaco', 'principio_activo': 'Diclofenaco', 'presentacion': 'Tableta', 'concentracion': '50mg', 'precio_unitario': 18.00, 'stock': 70, 'stock_minimo': 15, 'requiere_receta': True},
        
        # Antibióticos
        {'nombre': 'Amoxicilina', 'principio_activo': 'Amoxicilina', 'presentacion': 'Cápsula', 'concentracion': '500mg', 'precio_unitario': 35.00, 'stock': 60, 'stock_minimo': 10, 'requiere_receta': True},
        {'nombre': 'Azitromicina', 'principio_activo': 'Azitromicina', 'presentacion': 'Cápsula', 'concentracion': '500mg', 'precio_unitario': 65.00, 'stock': 30, 'stock_minimo': 5, 'requiere_receta': True},
        {'nombre': 'Ciprofloxacino', 'principio_activo': 'Ciprofloxacino', 'presentacion': 'Tableta', 'concentracion': '500mg', 'precio_unitario': 45.00, 'stock': 40, 'stock_minimo': 10, 'requiere_receta': True},
        {'nombre': 'Claritromicina', 'principio_activo': 'Claritromicina', 'presentacion': 'Tableta', 'concentracion': '500mg', 'precio_unitario': 55.00, 'stock': 25, 'stock_minimo': 5, 'requiere_receta': True},
        
        # Antihistamínicos
        {'nombre': 'Loratadina', 'principio_activo': 'Loratadina', 'presentacion': 'Tableta', 'concentracion': '10mg', 'precio_unitario': 12.80, 'stock': 45, 'stock_minimo': 10, 'requiere_receta': False},
        {'nombre': 'Cetirizina', 'principio_activo': 'Cetirizina', 'presentacion': 'Tableta', 'concentracion': '10mg', 'precio_unitario': 14.50, 'stock': 55, 'stock_minimo': 10, 'requiere_receta': False},
        
        # Gastrointestinales
        {'nombre': 'Omeprazol', 'principio_activo': 'Omeprazol', 'presentacion': 'Cápsula', 'concentracion': '20mg', 'precio_unitario': 28.50, 'stock': 35, 'stock_minimo': 8, 'requiere_receta': True},
        {'nombre': 'Pantoprazol', 'principio_activo': 'Pantoprazol', 'presentacion': 'Tableta', 'concentracion': '40mg', 'precio_unitario': 32.00, 'stock': 30, 'stock_minimo': 8, 'requiere_receta': True},
        {'nombre': 'Metoclopramida', 'principio_activo': 'Metoclopramida', 'presentacion': 'Tableta', 'concentracion': '10mg', 'precio_unitario': 20.00, 'stock': 40, 'stock_minimo': 10, 'requiere_receta': True},
        
        # Cardiovasculares
        {'nombre': 'Losartán', 'principio_activo': 'Losartán', 'presentacion': 'Tableta', 'concentracion': '50mg', 'precio_unitario': 45.00, 'stock': 50, 'stock_minimo': 10, 'requiere_receta': True},
        {'nombre': 'Enalapril', 'principio_activo': 'Enalapril', 'presentacion': 'Tableta', 'concentracion': '10mg', 'precio_unitario': 32.00, 'stock': 45, 'stock_minimo': 10, 'requiere_receta': True},
        {'nombre': 'Amlodipino', 'principio_activo': 'Amlodipino', 'presentacion': 'Tableta', 'concentracion': '5mg', 'precio_unitario': 38.00, 'stock': 40, 'stock_minimo': 10, 'requiere_receta': True},
        {'nombre': 'Metoprolol', 'principio_activo': 'Metoprolol', 'presentacion': 'Tableta', 'concentracion': '50mg', 'precio_unitario': 42.00, 'stock': 35, 'stock_minimo': 8, 'requiere_receta': True},
        
        # Respiratorios
        {'nombre': 'Salbutamol', 'principio_activo': 'Salbutamol', 'presentacion': 'Inhalador', 'concentracion': '100mcg', 'precio_unitario': 120.00, 'stock': 25, 'stock_minimo': 5, 'requiere_receta': True},
        {'nombre': 'Budesonida', 'principio_activo': 'Budesonida', 'presentacion': 'Inhalador', 'concentracion': '200mcg', 'precio_unitario': 150.00, 'stock': 20, 'stock_minimo': 5, 'requiere_receta': True},
        
        # Metabólicos
        {'nombre': 'Metformina', 'principio_activo': 'Metformina', 'presentacion': 'Tableta', 'concentracion': '850mg', 'precio_unitario': 38.00, 'stock': 40, 'stock_minimo': 10, 'requiere_receta': True},
        {'nombre': 'Insulina', 'principio_activo': 'Insulina', 'presentacion': 'Inyectable', 'concentracion': '100UI', 'precio_unitario': 200.00, 'stock': 15, 'stock_minimo': 5, 'requiere_receta': True},
        
        # Neurológicos
        {'nombre': 'Gabapentina', 'principio_activo': 'Gabapentina', 'presentacion': 'Cápsula', 'concentracion': '300mg', 'precio_unitario': 78.00, 'stock': 15, 'stock_minimo': 5, 'requiere_receta': True},
        {'nombre': 'Clonazepam', 'principio_activo': 'Clonazepam', 'presentacion': 'Tableta', 'concentracion': '2mg', 'precio_unitario': 55.00, 'stock': 20, 'stock_minimo': 5, 'requiere_receta': True},
        {'nombre': 'Diazepam', 'principio_activo': 'Diazepam', 'presentacion': 'Tableta', 'concentracion': '5mg', 'precio_unitario': 48.00, 'stock': 25, 'stock_minimo': 5, 'requiere_receta': True},
        
        # Diuréticos
        {'nombre': 'Furosemida', 'principio_activo': 'Furosemida', 'presentacion': 'Tableta', 'concentracion': '40mg', 'precio_unitario': 25.00, 'stock': 35, 'stock_minimo': 8, 'requiere_receta': True},
        {'nombre': 'Hidroclorotiazida', 'principio_activo': 'Hidroclorotiazida', 'presentacion': 'Tableta', 'concentracion': '25mg', 'precio_unitario': 22.00, 'stock': 40, 'stock_minimo': 10, 'requiere_receta': True},
        
        # Antiinflamatorios
        {'nombre': 'Prednisona', 'principio_activo': 'Prednisona', 'presentacion': 'Tableta', 'concentracion': '20mg', 'precio_unitario': 35.00, 'stock': 30, 'stock_minimo': 8, 'requiere_receta': True},
        {'nombre': 'Dexametasona', 'principio_activo': 'Dexametasona', 'presentacion': 'Tableta', 'concentracion': '4mg', 'precio_unitario': 40.00, 'stock': 25, 'stock_minimo': 5, 'requiere_receta': True},
        
        # Otros
        {'nombre': 'Sertralina', 'principio_activo': 'Sertralina', 'presentacion': 'Tableta', 'concentracion': '50mg', 'precio_unitario': 62.00, 'stock': 20, 'stock_minimo': 5, 'requiere_receta': True},
        {'nombre': 'Fluoxetina', 'principio_activo': 'Fluoxetina', 'presentacion': 'Cápsula', 'concentracion': '20mg', 'precio_unitario': 58.00, 'stock': 20, 'stock_minimo': 5, 'requiere_receta': True},
    ]
    
    # Agregar campos adicionales
    laboratorios = ['Bayer', 'Pfizer', 'Roche', 'Novartis', 'AstraZeneca', 'GSK', 'Sanofi']
    proveedores = ['Distribuidora Médica', 'Farmacéutica Nacional', 'ImporMed', 'MediSupply']
    
    for m in medicamentos:
        m['fecha_caducidad'] = (datetime.now() + timedelta(days=random.randint(60, 730))).strftime('%Y-%m-%d')
        m['activo'] = True
        m['laboratorio'] = random.choice(laboratorios)
        m['proveedor'] = random.choice(proveedores)
    
    # Eliminar datos existentes y insertar nuevos
    db.medicines.delete_many({})
    result = db.medicines.insert_many(medicamentos)
    print(f"✅ {len(result.inserted_ids)} medicamentos insertados")
    return len(result.inserted_ids)

def main():
    """Función principal."""
    print("="*60)
    print("🚀 INSERTANDO DATOS EN COLECCIONES VACÍAS")
    print("="*60)
    
    db = get_mongo_connection()
    
    # Insertar datos en cada colección
    total = 0
    
    # 1. Urgencias
    total += insert_emergencies(db, 100)
    
    # 2. Laboratorio
    total += insert_lab_requests(db, 150)
    
    # 3. Farmacia
    total += insert_medicines(db)
    
    # Mostrar resumen
    print("\n" + "="*60)
    print("📊 RESUMEN FINAL")
    print("="*60)
    print(f"  - Urgencias: {db.emergencies.count_documents({})}")
    print(f"  - Laboratorio: {db.lab_requests.count_documents({})}")
    print(f"  - Farmacia: {db.medicines.count_documents({})}")
    print(f"\n  TOTAL: {total} documentos insertados")
    
    print("\n" + "="*60)
    print("✅ DATOS INSERTADOS EXITOSAMENTE")
    print("="*60)
    print("\n🚀 Ahora ejecuta: python manage.py runserver")

if __name__ == "__main__":
    main()
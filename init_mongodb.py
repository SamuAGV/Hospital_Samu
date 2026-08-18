"""
Script para inicializar MongoDB con colecciones y datos de ejemplo
Ejecutar: python init_mongodb.py
"""

import os
import sys
import certifi
from datetime import datetime, timedelta
import random
from pymongo import MongoClient
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de MongoDB
MONGO_URI = os.getenv('MONGO_URI', 'mongodb+srv://Samu:mongodb@cluster0.gtzyuap.mongodb.net/')
MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', 'medinsight_hospital')

def get_mongo_connection():
    """Obtener conexión a MongoDB con manejo de SSL."""
    try:
        client = MongoClient(
            MONGO_URI,
            tlsCAFile=certifi.where(),
            serverSelectionTimeoutMS=10000
        )
        db = client[MONGO_DB_NAME]
        # Probar conexión
        client.admin.command('ping')
        print(f"✅ Conectado a MongoDB: {MONGO_DB_NAME}")
        return db
    except Exception as e:
        print(f"❌ Error conectando a MongoDB: {e}")
        print("Verifica que certifi esté instalado: pip install certifi")
        sys.exit(1)

def create_collections(db):
    """Crear todas las colecciones necesarias."""
    collections = [
        'patients',
        'doctors',
        'specialties',
        'appointments',
        'consultations',
        'diagnostics',
        'treatments',
        'hospitalizations',
        'emergencies',
        'lab_requests',
        'medicines',
        'inventory',
        'alerts',
        'users',
        'roles',
        'imported_files'
    ]
    
    existing = db.list_collection_names()
    for collection in collections:
        if collection not in existing:
            db.create_collection(collection)
            print(f"✅ Colección creada: {collection}")
        else:
            print(f"ℹ️ Colección ya existe: {collection}")
    
    # Crear índices para mejorar rendimiento
    create_indexes(db)

def create_indexes(db):
    """Crear índices para las colecciones."""
    try:
        # Índices para pacientes
        db.patients.create_index('id_paciente', unique=True)
        db.patients.create_index([('nombre', 1), ('apellido', 1)])
        db.patients.create_index('email', unique=True, sparse=True)
        db.patients.create_index('telefono', unique=True, sparse=True)
        
        # Índices para citas
        db.appointments.create_index('fecha_hora')
        db.appointments.create_index('estado')
        db.appointments.create_index('id_paciente')
        db.appointments.create_index('id_medico')
        
        # Índices para consultas
        db.consultations.create_index('fecha_hora')
        db.consultations.create_index('id_paciente')
        db.consultations.create_index('id_medico')
        
        # Índices para hospitalizaciones
        db.hospitalizations.create_index('estado')
        db.hospitalizations.create_index('fecha_ingreso')
        db.hospitalizations.create_index('id_paciente')
        
        # Índices para medicamentos
        db.medicines.create_index('nombre')
        db.medicines.create_index('stock')
        db.medicines.create_index('fecha_caducidad')
        
        print("✅ Índices creados correctamente")
    except Exception as e:
        print(f"⚠️ Error creando índices: {e}")

def insert_sample_data(db):
    """Insertar datos de ejemplo en las colecciones."""
    print("\n📝 Insertando datos de ejemplo...")
    
    # 1. Especialidades
    if db.specialties.count_documents({}) == 0:
        specialties = [
            {
                'id_especialidad': 1,
                'nombre': 'Medicina General',
                'descripcion': 'Atención primaria y consultas generales',
                'costo_consulta': 350.00,
                'tiempo_promedio_atencion': 30,
                'activo': True
            },
            {
                'id_especialidad': 2,
                'nombre': 'Cardiología',
                'descripcion': 'Diagnóstico y tratamiento de enfermedades del corazón',
                'costo_consulta': 650.00,
                'tiempo_promedio_atencion': 45,
                'activo': True
            },
            {
                'id_especialidad': 3,
                'nombre': 'Pediatría',
                'descripcion': 'Atención médica para niños y adolescentes',
                'costo_consulta': 400.00,
                'tiempo_promedio_atencion': 30,
                'activo': True
            },
            {
                'id_especialidad': 4,
                'nombre': 'Ginecología',
                'descripcion': 'Salud de la mujer y sistema reproductor',
                'costo_consulta': 550.00,
                'tiempo_promedio_atencion': 40,
                'activo': True
            },
            {
                'id_especialidad': 5,
                'nombre': 'Traumatología',
                'descripcion': 'Lesiones del sistema musculoesquelético',
                'costo_consulta': 500.00,
                'tiempo_promedio_atencion': 35,
                'activo': True
            },
            {
                'id_especialidad': 6,
                'nombre': 'Neurología',
                'descripcion': 'Trastornos del sistema nervioso',
                'costo_consulta': 700.00,
                'tiempo_promedio_atencion': 50,
                'activo': True
            },
            {
                'id_especialidad': 7,
                'nombre': 'Dermatología',
                'descripcion': 'Enfermedades de la piel',
                'costo_consulta': 450.00,
                'tiempo_promedio_atencion': 30,
                'activo': True
            }
        ]
        db.specialties.insert_many(specialties)
        print("✅ Especialidades insertadas")
    
    # 2. Médicos
    if db.doctors.count_documents({}) == 0:
        doctors = [
            {
                'id_medico': 1,
                'nombre': 'Carlos',
                'apellido': 'Ramírez',
                'id_especialidad': 1,
                'cedula_profesional': 'MED-001',
                'telefono': '555-1001',
                'email': 'carlos.ramirez@hospital.com',
                'fecha_contratacion': '2020-01-15',
                'activo': True
            },
            {
                'id_medico': 2,
                'nombre': 'Ana',
                'apellido': 'Martínez',
                'id_especialidad': 2,
                'cedula_profesional': 'MED-002',
                'telefono': '555-1002',
                'email': 'ana.martinez@hospital.com',
                'fecha_contratacion': '2019-03-10',
                'activo': True
            },
            {
                'id_medico': 3,
                'nombre': 'Roberto',
                'apellido': 'Sánchez',
                'id_especialidad': 3,
                'cedula_profesional': 'MED-003',
                'telefono': '555-1003',
                'email': 'roberto.sanchez@hospital.com',
                'fecha_contratacion': '2021-06-01',
                'activo': True
            },
            {
                'id_medico': 4,
                'nombre': 'Laura',
                'apellido': 'Gómez',
                'id_especialidad': 4,
                'cedula_profesional': 'MED-004',
                'telefono': '555-1004',
                'email': 'laura.gomez@hospital.com',
                'fecha_contratacion': '2020-09-15',
                'activo': True
            },
            {
                'id_medico': 5,
                'nombre': 'Jorge',
                'apellido': 'Hernández',
                'id_especialidad': 5,
                'cedula_profesional': 'MED-005',
                'telefono': '555-1005',
                'email': 'jorge.hernandez@hospital.com',
                'fecha_contratacion': '2018-11-20',
                'activo': True
            }
        ]
        db.doctors.insert_many(doctors)
        print("✅ Médicos insertados")
    
    # 3. Pacientes
    if db.patients.count_documents({}) == 0:
        patients = [
            {
                'id_paciente': 1,
                'nombre': 'María',
                'apellido': 'González',
                'fecha_nacimiento': '1985-03-15',
                'genero': 'Femenino',
                'telefono': '555-2001',
                'email': 'maria.gonzalez@email.com',
                'direccion': 'Calle Principal #123',
                'tipo_sangre': 'O+',
                'alergias': 'Penicilina',
                'enfermedades_cronicas': 'Diabetes Tipo 2',
                'fecha_registro': datetime.now().isoformat(),
                'activo': True,
                'edad': 39
            },
            {
                'id_paciente': 2,
                'nombre': 'Juan',
                'apellido': 'Pérez',
                'fecha_nacimiento': '1990-07-22',
                'genero': 'Masculino',
                'telefono': '555-2002',
                'email': 'juan.perez@email.com',
                'direccion': 'Avenida Reforma #456',
                'tipo_sangre': 'A+',
                'alergias': 'Ninguna',
                'enfermedades_cronicas': 'Ninguna',
                'fecha_registro': datetime.now().isoformat(),
                'activo': True,
                'edad': 34
            },
            {
                'id_paciente': 3,
                'nombre': 'Ana',
                'apellido': 'López',
                'fecha_nacimiento': '1978-11-02',
                'genero': 'Femenino',
                'telefono': '555-2003',
                'email': 'ana.lopez@email.com',
                'direccion': 'Calle Insurgentes #789',
                'tipo_sangre': 'B-',
                'alergias': 'Polen',
                'enfermedades_cronicas': 'Hipertensión',
                'fecha_registro': datetime.now().isoformat(),
                'activo': True,
                'edad': 46
            },
            {
                'id_paciente': 4,
                'nombre': 'Pedro',
                'apellido': 'Ramírez',
                'fecha_nacimiento': '1965-05-30',
                'genero': 'Masculino',
                'telefono': '555-2004',
                'email': 'pedro.ramirez@email.com',
                'direccion': 'Avenida Juárez #321',
                'tipo_sangre': 'AB+',
                'alergias': 'Ninguna',
                'enfermedades_cronicas': 'Cardiopatía',
                'fecha_registro': datetime.now().isoformat(),
                'activo': True,
                'edad': 59
            },
            {
                'id_paciente': 5,
                'nombre': 'Laura',
                'apellido': 'Martínez',
                'fecha_nacimiento': '1995-09-12',
                'genero': 'Femenino',
                'telefono': '555-2005',
                'email': 'laura.martinez@email.com',
                'direccion': 'Calle Constitución #654',
                'tipo_sangre': 'O-',
                'alergias': 'Lácteos',
                'enfermedades_cronicas': 'Ninguna',
                'fecha_registro': datetime.now().isoformat(),
                'activo': True,
                'edad': 29
            }
        ]
        db.patients.insert_many(patients)
        print("✅ Pacientes insertados")
    
    # 4. Medicamentos
    if db.medicines.count_documents({}) == 0:
        medicines = [
            {
                'id_medicamento': 1,
                'nombre': 'Paracetamol',
                'principio_activo': 'Acetaminofén',
                'presentacion': 'Tableta',
                'concentracion': '500mg',
                'precio_unitario': 15.50,
                'stock': 100,
                'stock_minimo': 20,
                'requiere_receta': False,
                'fecha_caducidad': '2027-12-31',
                'activo': True
            },
            {
                'id_medicamento': 2,
                'nombre': 'Ibuprofeno',
                'principio_activo': 'Ibuprofeno',
                'presentacion': 'Tableta',
                'concentracion': '400mg',
                'precio_unitario': 22.30,
                'stock': 80,
                'stock_minimo': 15,
                'requiere_receta': False,
                'fecha_caducidad': '2027-10-15',
                'activo': True
            },
            {
                'id_medicamento': 3,
                'nombre': 'Amoxicilina',
                'principio_activo': 'Amoxicilina',
                'presentacion': 'Cápsula',
                'concentracion': '500mg',
                'precio_unitario': 35.00,
                'stock': 60,
                'stock_minimo': 10,
                'requiere_receta': True,
                'fecha_caducidad': '2027-08-20',
                'activo': True
            },
            {
                'id_medicamento': 4,
                'nombre': 'Loratadina',
                'principio_activo': 'Loratadina',
                'presentacion': 'Tableta',
                'concentracion': '10mg',
                'precio_unitario': 12.80,
                'stock': 45,
                'stock_minimo': 10,
                'requiere_receta': False,
                'fecha_caducidad': '2028-01-31',
                'activo': True
            },
            {
                'id_medicamento': 5,
                'nombre': 'Omeprazol',
                'principio_activo': 'Omeprazol',
                'presentacion': 'Cápsula',
                'concentracion': '20mg',
                'precio_unitario': 28.50,
                'stock': 35,
                'stock_minimo': 8,
                'requiere_receta': True,
                'fecha_caducidad': '2027-09-30',
                'activo': True
            }
        ]
        db.medicines.insert_many(medicines)
        print("✅ Medicamentos insertados")
    
    # 5. Citas de ejemplo
    if db.appointments.count_documents({}) == 0:
        today = datetime.now()
        appointments = []
        estados = ['Programada', 'Programada', 'Programada', 'Atendida', 'Cancelada']
        for i in range(15):
            fecha = today + timedelta(days=i % 5, hours=random.randint(8, 18))
            appointments.append({
                'id_paciente': random.randint(1, 5),
                'id_medico': random.randint(1, 5),
                'fecha_hora': fecha.isoformat(),
                'duracion': 30,
                'estado': random.choice(estados),
                'motivo': f'Consulta de seguimiento {i+1}',
                'fecha_registro': datetime.now().isoformat(),
                'especialidad': random.choice(['Medicina General', 'Cardiología', 'Pediatría'])
            })
        db.appointments.insert_many(appointments)
        print("✅ Citas de ejemplo insertadas")
    
    # 6. Consultas de ejemplo
    if db.consultations.count_documents({}) == 0:
        consultations = []
        for i in range(10):
            fecha = datetime.now() - timedelta(days=random.randint(0, 30))
            consultations.append({
                'id_paciente': random.randint(1, 5),
                'id_medico': random.randint(1, 5),
                'fecha_hora': fecha.isoformat(),
                'peso': round(random.uniform(50, 100), 1),
                'altura': round(random.uniform(150, 190), 1),
                'presion_arterial': f"{random.randint(110, 140)}/{random.randint(70, 90)}",
                'temperatura': round(random.uniform(36.0, 38.5), 1),
                'frecuencia_cardiaca': random.randint(60, 100),
                'sintomas': random.choice(['Dolor de cabeza', 'Fiebre', 'Dolor abdominal', 'Tos', 'Cansancio']),
                'notas_clinicas': 'Paciente en buen estado general',
                'tipo_consulta': random.choice(['Primera vez', 'Seguimiento', 'Urgencia']),
                'duracion_atencion': random.randint(15, 45),
                'especialidad': random.choice(['Medicina General', 'Cardiología', 'Pediatría'])
            })
        db.consultations.insert_many(consultations)
        print("✅ Consultas de ejemplo insertadas")
    
    # 7. Hospitalizaciones activas
    if db.hospitalizations.count_documents({}) == 0:
        hospitalizations = [
            {
                'id_paciente': 3,
                'id_medico_responsable': 1,
                'fecha_ingreso': (datetime.now() - timedelta(days=2)).isoformat(),
                'habitacion': '301',
                'cama': 'A',
                'motivo_ingreso': 'Dolor abdominal agudo',
                'diagnostico_ingreso': 'Apendicitis aguda',
                'tipo_ingreso': 'Urgencia',
                'estado': 'Activa',
                'observaciones': 'Paciente en observación'
            },
            {
                'id_paciente': 4,
                'id_medico_responsable': 2,
                'fecha_ingreso': (datetime.now() - timedelta(days=5)).isoformat(),
                'habitacion': '205',
                'cama': 'B',
                'motivo_ingreso': 'Dolor en el pecho',
                'diagnostico_ingreso': 'Angina de pecho',
                'tipo_ingreso': 'Urgencia',
                'estado': 'Activa',
                'observaciones': 'En espera de estudios'
            }
        ]
        db.hospitalizations.insert_many(hospitalizations)
        print("✅ Hospitalizaciones activas insertadas")
    
    print("\n✅ Datos de ejemplo insertados correctamente")

def main():
    """Función principal."""
    print("=" * 60)
    print("🚀 INICIALIZANDO MONGODB PARA MEDINSIGHT HOSPITAL")
    print("=" * 60)
    
    # Conectar a MongoDB
    db = get_mongo_connection()
    
    # Crear colecciones
    print("\n📁 Creando colecciones...")
    create_collections(db)
    
    # Insertar datos de ejemplo
    insert_sample_data(db)
    
    # Mostrar resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE COLECCIONES")
    print("=" * 60)
    collections = db.list_collection_names()
    for coll in collections:
        count = db[coll].count_documents({})
        print(f"  {coll}: {count} documentos")
    
    print("\n" + "=" * 60)
    print("✅ INICIALIZACIÓN COMPLETADA")
    print("=" * 60)
    print("\nAhora puedes ejecutar:")
    print("  python manage.py runserver")
    print("  http://localhost:8000/")

if __name__ == "__main__":
    main()
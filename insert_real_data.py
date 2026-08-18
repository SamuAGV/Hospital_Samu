"""
Script para insertar datos reales de prueba en MongoDB
Ejecutar: python insert_real_data.py
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

def insert_real_data(db):
    print("\n📝 Insertando datos reales de prueba...")
    
    # 1. LIMPIAR DATOS EXISTENTES (OPCIONAL - DESCOMENTAR PARA LIMPIAR)
    # print("Limpiando datos existentes...")
    # db.patients.delete_many({})
    # db.doctors.delete_many({})
    # db.specialties.delete_many({})
    # db.appointments.delete_many({})
    # db.consultations.delete_many({})
    # db.hospitalizations.delete_many({})
    
    # 2. ESPECIALIDADES
    specialties = [
        {'nombre': 'Medicina General', 'descripcion': 'Atención primaria y consultas generales', 'costo_consulta': 350, 'tiempo_promedio_atencion': 30, 'activo': True},
        {'nombre': 'Cardiología', 'descripcion': 'Diagnóstico y tratamiento de enfermedades del corazón', 'costo_consulta': 650, 'tiempo_promedio_atencion': 45, 'activo': True},
        {'nombre': 'Pediatría', 'descripcion': 'Atención médica para niños y adolescentes', 'costo_consulta': 400, 'tiempo_promedio_atencion': 30, 'activo': True},
        {'nombre': 'Ginecología', 'descripcion': 'Salud de la mujer y sistema reproductor', 'costo_consulta': 550, 'tiempo_promedio_atencion': 40, 'activo': True},
        {'nombre': 'Traumatología', 'descripcion': 'Lesiones del sistema musculoesquelético', 'costo_consulta': 500, 'tiempo_promedio_atencion': 35, 'activo': True},
        {'nombre': 'Neurología', 'descripcion': 'Trastornos del sistema nervioso', 'costo_consulta': 700, 'tiempo_promedio_atencion': 50, 'activo': True},
        {'nombre': 'Dermatología', 'descripcion': 'Enfermedades de la piel', 'costo_consulta': 450, 'tiempo_promedio_atencion': 30, 'activo': True},
    ]
    db.specialties.insert_many(specialties)
    print(f"✅ {len(specialties)} especialidades insertadas")
    
    # 3. MÉDICOS
    doctors = [
        {'nombre': 'Carlos', 'apellido': 'Ramírez', 'especialidad': 'Medicina General', 'cedula_profesional': 'MED-001', 'telefono': '555-1001', 'email': 'carlos@hospital.com', 'activo': True},
        {'nombre': 'Ana', 'apellido': 'Martínez', 'especialidad': 'Cardiología', 'cedula_profesional': 'MED-002', 'telefono': '555-1002', 'email': 'ana@hospital.com', 'activo': True},
        {'nombre': 'Roberto', 'apellido': 'Sánchez', 'especialidad': 'Pediatría', 'cedula_profesional': 'MED-003', 'telefono': '555-1003', 'email': 'roberto@hospital.com', 'activo': True},
        {'nombre': 'Laura', 'apellido': 'Gómez', 'especialidad': 'Ginecología', 'cedula_profesional': 'MED-004', 'telefono': '555-1004', 'email': 'laura@hospital.com', 'activo': True},
        {'nombre': 'Jorge', 'apellido': 'Hernández', 'especialidad': 'Traumatología', 'cedula_profesional': 'MED-005', 'telefono': '555-1005', 'email': 'jorge@hospital.com', 'activo': True},
        {'nombre': 'Patricia', 'apellido': 'Díaz', 'especialidad': 'Neurología', 'cedula_profesional': 'MED-006', 'telefono': '555-1006', 'email': 'patricia@hospital.com', 'activo': True},
        {'nombre': 'Miguel', 'apellido': 'Torres', 'especialidad': 'Dermatología', 'cedula_profesional': 'MED-007', 'telefono': '555-1007', 'email': 'miguel@hospital.com', 'activo': True},
    ]
    db.doctors.insert_many(doctors)
    print(f"✅ {len(doctors)} médicos insertados")
    
    # 4. PACIENTES (50 pacientes)
    nombres = ['María', 'Juan', 'Ana', 'Pedro', 'Laura', 'Carlos', 'Carmen', 'José', 'Isabel', 'Francisco',
               'Teresa', 'Manuel', 'Elena', 'Antonio', 'Rosa', 'Javier', 'Dolores', 'Luis', 'Pilar', 'Miguel',
               'Sofía', 'David', 'Marta', 'Daniel', 'Lucía', 'Alejandro', 'Paula', 'Jesús', 'Eva', 'Rafael']
    apellidos = ['González', 'Pérez', 'López', 'Ramírez', 'Martínez', 'Sánchez', 'Gómez', 'Fernández', 'Díaz', 'Torres',
                 'Romero', 'Alvarez', 'Castillo', 'Morales', 'Reyes', 'Cruz', 'Ortiz', 'Ramos', 'Mendoza', 'Herrera']
    tipos_sangre = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    
    patients = []
    for i in range(50):
        nombre = random.choice(nombres)
        apellido = random.choice(apellidos)
        edad = random.randint(18, 85)
        fecha_nac = datetime.now() - timedelta(days=edad*365 + random.randint(0, 365))
        
        patients.append({
            'nombre': nombre,
            'apellido': apellido,
            'fecha_nacimiento': fecha_nac.strftime('%Y-%m-%d'),
            'genero': random.choice(['Masculino', 'Femenino']),
            'telefono': f'555-{random.randint(1000, 9999)}',
            'email': f'{nombre.lower()}.{apellido.lower()}@email.com',
            'direccion': f'Calle {random.randint(1, 500)} #{random.randint(1, 100)}',
            'tipo_sangre': random.choice(tipos_sangre),
            'alergias': random.choice(['Ninguna', 'Penicilina', 'Polen', 'Lácteos', 'Medicamentos']),
            'enfermedades_cronicas': random.choice(['Ninguna', 'Diabetes', 'Hipertensión', 'Cardiopatía', 'Asma']),
            'fecha_registro': datetime.now().isoformat(),
            'activo': True,
            'edad': edad
        })
    db.patients.insert_many(patients)
    print(f"✅ {len(patients)} pacientes insertados")
    
    # 5. CITAS (100 citas)
    appointments = []
    estados = ['Programada', 'Programada', 'Programada', 'Atendida', 'Cancelada', 'Reprogramada']
    for i in range(100):
        fecha = datetime.now() + timedelta(days=random.randint(-30, 30), hours=random.randint(8, 18))
        appointments.append({
            'id_paciente': random.randint(1, 50),
            'id_medico': random.randint(1, 7),
            'especialidad': random.choice([s['nombre'] for s in specialties]),
            'fecha_hora': fecha.isoformat(),
            'duracion': 30,
            'estado': random.choice(estados),
            'motivo': random.choice(['Consulta general', 'Dolor de cabeza', 'Chequeo anual', 'Dolor abdominal', 'Seguimiento']),
            'fecha_registro': datetime.now().isoformat()
        })
    db.appointments.insert_many(appointments)
    print(f"✅ {len(appointments)} citas insertadas")
    
    # 6. CONSULTAS (200 consultas)
    consultations = []
    sintomas = ['Dolor de cabeza', 'Fiebre', 'Dolor abdominal', 'Tos persistente', 'Cansancio', 
                'Dolor en el pecho', 'Mareos', 'Náuseas', 'Dolor muscular', 'Falta de aire']
    tipos = ['Primera vez', 'Seguimiento', 'Urgencia']
    
    for i in range(200):
        fecha = datetime.now() - timedelta(days=random.randint(0, 90), hours=random.randint(8, 18))
        consultations.append({
            'id_paciente': random.randint(1, 50),
            'id_medico': random.randint(1, 7),
            'especialidad': random.choice([s['nombre'] for s in specialties]),
            'fecha_hora': fecha.isoformat(),
            'peso': round(random.uniform(50, 100), 1),
            'altura': round(random.uniform(150, 190), 1),
            'presion_arterial': f"{random.randint(110, 140)}/{random.randint(70, 90)}",
            'temperatura': round(random.uniform(36.0, 38.5), 1),
            'frecuencia_cardiaca': random.randint(60, 100),
            'sintomas': random.choice(sintomas),
            'notas_clinicas': random.choice(['Paciente en buen estado', 'Requiere seguimiento', 'Remitido a especialista', 'Ninguna']),
            'tipo_consulta': random.choice(tipos),
            'duracion_atencion': random.randint(15, 60)
        })
    db.consultations.insert_many(consultations)
    print(f"✅ {len(consultations)} consultas insertadas")
    
    # 7. HOSPITALIZACIONES (20 hospitalizaciones)
    hospitalizations = []
    for i in range(20):
        fecha_ingreso = datetime.now() - timedelta(days=random.randint(0, 15))
        fecha_alta = fecha_ingreso + timedelta(days=random.randint(1, 10)) if random.random() > 0.3 else None
        
        hospitalizations.append({
            'id_paciente': random.randint(1, 50),
            'id_medico_responsable': random.randint(1, 7),
            'fecha_ingreso': fecha_ingreso.isoformat(),
            'fecha_alta': fecha_alta.isoformat() if fecha_alta else None,
            'habitacion': f'{random.randint(1, 5)}0{random.randint(1, 9)}',
            'cama': random.choice(['A', 'B', 'C']),
            'motivo_ingreso': random.choice(['Dolor abdominal', 'Dolor en el pecho', 'Fractura', 'Infección', 'Cirugía programada']),
            'diagnostico_ingreso': random.choice(['Apendicitis', 'Angina', 'Fractura de fémur', 'Neumonía', 'Colecistitis']),
            'tipo_ingreso': random.choice(['Programado', 'Urgencia']),
            'estado': 'Activa' if fecha_alta is None else 'Alta',
            'observaciones': random.choice(['Paciente estable', 'En recuperación', 'Requiere cirugía', 'Observación']),
            'especialidad': random.choice([s['nombre'] for s in specialties])
        })
    db.hospitalizations.insert_many(hospitalizations)
    print(f"✅ {len(hospitalizations)} hospitalizaciones insertadas")
    
    print("\n✅ Datos reales de prueba insertados correctamente")
    
    # Mostrar resumen
    print("\n📊 RESUMEN DE DATOS:")
    print(f"  - Especialidades: {db.specialties.count_documents({})}")
    print(f"  - Médicos: {db.doctors.count_documents({})}")
    print(f"  - Pacientes: {db.patients.count_documents({})}")
    print(f"  - Citas: {db.appointments.count_documents({})}")
    print(f"  - Consultas: {db.consultations.count_documents({})}")
    print(f"  - Hospitalizaciones: {db.hospitalizations.count_documents({})}")
    
    # Mostrar pacientes activos
    activos = db.patients.count_documents({'activo': True})
    print(f"  - Pacientes activos: {activos}")

if __name__ == "__main__":
    db = get_mongo_connection()
    insert_real_data(db)
    print("\n✅ Proceso completado")
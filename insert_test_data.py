"""
Script para insertar datos de prueba en MongoDB
Ejecutar: python insert_test_data.py
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

def insert_test_data(db):
    print("\n📝 Insertando datos de prueba...")
    
    # 1. Limpiar colecciones existentes (opcional)
    # db.patients.delete_many({})
    # db.doctors.delete_many({})
    # db.specialties.delete_many({})
    # db.appointments.delete_many({})
    # db.consultations.delete_many({})
    # db.hospitalizations.delete_many({})
    
    # 2. Especialidades
    if db.specialties.count_documents({}) == 0:
        specialties = [
            {'id_especialidad': 1, 'nombre': 'Medicina General', 'descripcion': 'Atención primaria', 'costo_consulta': 350, 'tiempo_promedio_atencion': 30, 'activo': True},
            {'id_especialidad': 2, 'nombre': 'Cardiología', 'descripcion': 'Enfermedades del corazón', 'costo_consulta': 650, 'tiempo_promedio_atencion': 45, 'activo': True},
            {'id_especialidad': 3, 'nombre': 'Pediatría', 'descripcion': 'Atención infantil', 'costo_consulta': 400, 'tiempo_promedio_atencion': 30, 'activo': True},
            {'id_especialidad': 4, 'nombre': 'Ginecología', 'descripcion': 'Salud de la mujer', 'costo_consulta': 550, 'tiempo_promedio_atencion': 40, 'activo': True},
            {'id_especialidad': 5, 'nombre': 'Traumatología', 'descripcion': 'Lesiones óseas', 'costo_consulta': 500, 'tiempo_promedio_atencion': 35, 'activo': True},
        ]
        db.specialties.insert_many(specialties)
        print("✅ Especialidades insertadas")
    
    # 3. Médicos
    if db.doctors.count_documents({}) == 0:
        doctors = [
            {'id_medico': 1, 'nombre': 'Carlos', 'apellido': 'Ramírez', 'id_especialidad': 1, 'cedula_profesional': 'MED-001', 'telefono': '555-1001', 'email': 'carlos@hospital.com', 'activo': True},
            {'id_medico': 2, 'nombre': 'Ana', 'apellido': 'Martínez', 'id_especialidad': 2, 'cedula_profesional': 'MED-002', 'telefono': '555-1002', 'email': 'ana@hospital.com', 'activo': True},
            {'id_medico': 3, 'nombre': 'Roberto', 'apellido': 'Sánchez', 'id_especialidad': 3, 'cedula_profesional': 'MED-003', 'telefono': '555-1003', 'email': 'roberto@hospital.com', 'activo': True},
            {'id_medico': 4, 'nombre': 'Laura', 'apellido': 'Gómez', 'id_especialidad': 4, 'cedula_profesional': 'MED-004', 'telefono': '555-1004', 'email': 'laura@hospital.com', 'activo': True},
            {'id_medico': 5, 'nombre': 'Jorge', 'apellido': 'Hernández', 'id_especialidad': 5, 'cedula_profesional': 'MED-005', 'telefono': '555-1005', 'email': 'jorge@hospital.com', 'activo': True},
        ]
        db.doctors.insert_many(doctors)
        print("✅ Médicos insertados")
    
    # 4. Pacientes
    if db.patients.count_documents({}) == 0:
        patients = [
            {'id_paciente': 1, 'nombre': 'María', 'apellido': 'González', 'fecha_nacimiento': '1985-03-15', 'genero': 'Femenino', 'telefono': '555-2001', 'email': 'maria@email.com', 'tipo_sangre': 'O+', 'alergias': 'Penicilina', 'enfermedades_cronicas': 'Diabetes', 'activo': True, 'edad': 39},
            {'id_paciente': 2, 'nombre': 'Juan', 'apellido': 'Pérez', 'fecha_nacimiento': '1990-07-22', 'genero': 'Masculino', 'telefono': '555-2002', 'email': 'juan@email.com', 'tipo_sangre': 'A+', 'alergias': 'Ninguna', 'enfermedades_cronicas': 'Ninguna', 'activo': True, 'edad': 34},
            {'id_paciente': 3, 'nombre': 'Ana', 'apellido': 'López', 'fecha_nacimiento': '1978-11-02', 'genero': 'Femenino', 'telefono': '555-2003', 'email': 'ana@email.com', 'tipo_sangre': 'B-', 'alergias': 'Polen', 'enfermedades_cronicas': 'Hipertensión', 'activo': True, 'edad': 46},
            {'id_paciente': 4, 'nombre': 'Pedro', 'apellido': 'Ramírez', 'fecha_nacimiento': '1965-05-30', 'genero': 'Masculino', 'telefono': '555-2004', 'email': 'pedro@email.com', 'tipo_sangre': 'AB+', 'alergias': 'Ninguna', 'enfermedades_cronicas': 'Cardiopatía', 'activo': True, 'edad': 59},
            {'id_paciente': 5, 'nombre': 'Laura', 'apellido': 'Martínez', 'fecha_nacimiento': '1995-09-12', 'genero': 'Femenino', 'telefono': '555-2005', 'email': 'laura@email.com', 'tipo_sangre': 'O-', 'alergias': 'Lácteos', 'enfermedades_cronicas': 'Ninguna', 'activo': True, 'edad': 29},
        ]
        db.patients.insert_many(patients)
        print("✅ Pacientes insertados")
    
    # 5. Citas
    if db.appointments.count_documents({}) == 0:
        today = datetime.now()
        appointments = []
        estados = ['Programada', 'Programada', 'Programada', 'Atendida', 'Cancelada']
        for i in range(15):
            fecha = today + timedelta(days=random.randint(0, 10), hours=random.randint(8, 18))
            appointments.append({
                'id_paciente': random.randint(1, 5),
                'id_medico': random.randint(1, 5),
                'fecha_hora': fecha.isoformat(),
                'duracion': 30,
                'estado': random.choice(estados),
                'motivo': f'Consulta {i+1}',
                'fecha_registro': datetime.now().isoformat()
            })
        db.appointments.insert_many(appointments)
        print("✅ Citas insertadas")
    
    # 6. Consultas
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
                'sintomas': random.choice(['Dolor de cabeza', 'Fiebre', 'Dolor abdominal', 'Tos']),
                'notas_clinicas': 'Paciente en buen estado',
                'tipo_consulta': random.choice(['Primera vez', 'Seguimiento']),
                'duracion_atencion': random.randint(15, 45)
            })
        db.consultations.insert_many(consultations)
        print("✅ Consultas insertadas")
    
    # 7. Hospitalizaciones
    if db.hospitalizations.count_documents({}) == 0:
        hospitalizations = [
            {'id_paciente': 3, 'id_medico_responsable': 1, 'fecha_ingreso': (datetime.now() - timedelta(days=2)).isoformat(), 'habitacion': '301', 'cama': 'A', 'motivo_ingreso': 'Dolor abdominal', 'diagnostico_ingreso': 'Apendicitis', 'tipo_ingreso': 'Urgencia', 'estado': 'Activa'},
            {'id_paciente': 4, 'id_medico_responsable': 2, 'fecha_ingreso': (datetime.now() - timedelta(days=5)).isoformat(), 'habitacion': '205', 'cama': 'B', 'motivo_ingreso': 'Dolor en el pecho', 'diagnostico_ingreso': 'Angina', 'tipo_ingreso': 'Urgencia', 'estado': 'Activa'},
        ]
        db.hospitalizations.insert_many(hospitalizations)
        print("✅ Hospitalizaciones insertadas")
    
    print("\n✅ Datos de prueba insertados correctamente")

if __name__ == "__main__":
    db = get_mongo_connection()
    insert_test_data(db)
    print("\n✅ Proceso completado")
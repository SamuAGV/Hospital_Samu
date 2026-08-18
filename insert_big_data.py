"""
Script para insertar MILES de datos reales en MongoDB
Ejecutar: python insert_big_data.py
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

def drop_all_indexes(db):
    """Eliminar todos los índices de las colecciones."""
    print("\n🗑️  Eliminando índices existentes...")
    collections = ['patients', 'doctors', 'appointments', 'consultations', 'hospitalizations', 'medicines']
    for coll_name in collections:
        if coll_name in db.list_collection_names():
            try:
                # Eliminar todos los índices excepto _id_
                db[coll_name].drop_indexes()
                print(f"   ✅ Índices eliminados de {coll_name}")
            except Exception as e:
                print(f"   ⚠️ Error eliminando índices de {coll_name}: {e}")

def generate_patients(count=1200):
    """Generar pacientes SIN campo id_paciente."""
    nombres = ['María', 'Juan', 'Ana', 'Pedro', 'Laura', 'Carlos', 'Carmen', 'José', 'Isabel', 'Francisco',
               'Teresa', 'Manuel', 'Elena', 'Antonio', 'Rosa', 'Javier', 'Dolores', 'Luis', 'Pilar', 'Miguel',
               'Sofía', 'David', 'Marta', 'Daniel', 'Lucía', 'Alejandro', 'Paula', 'Jesús', 'Eva', 'Rafael',
               'Raúl', 'Mónica', 'Alberto', 'Cristina', 'Fernando', 'Patricia', 'Sergio', 'Andrea', 'Ricardo', 'Beatriz',
               'Jorge', 'Ángela', 'Roberto', 'Silvia', 'Hugo', 'Verónica', 'Arturo', 'Lorena', 'Enrique', 'Claudia']
    apellidos = ['González', 'Pérez', 'López', 'Ramírez', 'Martínez', 'Sánchez', 'Gómez', 'Fernández', 'Díaz', 'Torres',
                 'Romero', 'Alvarez', 'Castillo', 'Morales', 'Reyes', 'Cruz', 'Ortiz', 'Ramos', 'Mendoza', 'Herrera',
                 'García', 'Rodríguez', 'Hernández', 'Jiménez', 'Ruiz', 'Molina', 'Muñoz', 'Perea', 'Domínguez',
                 'Vázquez', 'Serrano', 'Salazar', 'Núñez', 'Rojas', 'Campos', 'Duran', 'Hidalgo', 'Mora', 'Luna']
    tipos_sangre = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    generos = ['Masculino', 'Femenino']
    alergias = ['Ninguna', 'Penicilina', 'Polen', 'Lácteos', 'Medicamentos', 'Mariscos', 'Huevo']
    enfermedades = ['Ninguna', 'Diabetes Tipo 2', 'Hipertensión', 'Cardiopatía', 'Asma', 'Artritis', 'Cáncer', 'EPOC']
    ciudades = ['Ciudad de México', 'Guadalajara', 'Monterrey', 'Puebla', 'Tijuana', 'Querétaro', 
                'León', 'Zapopan', 'Mexicali', 'Aguascalientes', 'Morelia', 'Hermosillo']
    
    patients = []
    for i in range(count):
        nombre = random.choice(nombres)
        apellido = random.choice(apellidos)
        edad = random.randint(18, 95)
        fecha_nac = datetime.now() - timedelta(days=edad*365 + random.randint(0, 365))
        genero = random.choice(generos)
        
        patients.append({
            'nombre': nombre,
            'apellido': apellido,
            'fecha_nacimiento': fecha_nac.strftime('%Y-%m-%d'),
            'genero': genero,
            'telefono': f'555-{random.randint(1000, 9999)}',
            'email': f'{nombre.lower()}.{apellido.lower()}{random.randint(1, 9999)}@email.com',
            'direccion': f'{random.choice(["Calle", "Avenida", "Boulevard", "Cerrada", "Privada"])} {random.choice(["Principal", "Reforma", "Insurgentes", "Juárez", "Morelos"])} #{random.randint(1, 500)}',
            'tipo_sangre': random.choice(tipos_sangre),
            'alergias': random.choice(alergias),
            'enfermedades_cronicas': random.choice(enfermedades),
            'fecha_registro': (datetime.now() - timedelta(days=random.randint(0, 365))).isoformat(),
            'activo': random.random() > 0.1,
            'edad': edad,
            'ciudad': random.choice(ciudades)
        })
    return patients

def generate_doctors(count=50):
    """Generar médicos SIN campo id_medico."""
    nombres = ['Carlos', 'Ana', 'Roberto', 'Laura', 'Jorge', 'Patricia', 'Miguel', 'Elena', 'Fernando', 'Mónica',
               'Ricardo', 'Cristina', 'Sergio', 'Andrea', 'Hugo', 'Verónica', 'Arturo', 'Lorena', 'Enrique', 'Claudia',
               'Raúl', 'María', 'Alberto', 'Carmen', 'Luis', 'Dolores', 'Javier', 'Teresa', 'Manuel', 'Rosa']
    apellidos = ['Ramírez', 'Martínez', 'Sánchez', 'Gómez', 'Fernández', 'Díaz', 'Torres', 'Romero', 'Alvarez', 'Castillo',
                 'Morales', 'Reyes', 'Cruz', 'Ortiz', 'Ramos', 'Mendoza', 'Herrera', 'García', 'Rodríguez', 'Hernández']
    especialidades = ['Medicina General', 'Cardiología', 'Pediatría', 'Ginecología', 'Traumatología', 
                      'Neurología', 'Dermatología', 'Oftalmología', 'Otorrinolaringología', 'Urología',
                      'Psiquiatría', 'Reumatología', 'Endocrinología', 'Oncología', 'Neumología']
    
    doctors = []
    used_cedulas = set()
    for i in range(count):
        nombre = random.choice(nombres)
        apellido = random.choice(apellidos)
        especialidad = random.choice(especialidades)
        
        cedula = f'MED-{random.randint(10000, 99999)}'
        while cedula in used_cedulas:
            cedula = f'MED-{random.randint(10000, 99999)}'
        used_cedulas.add(cedula)
        
        doctors.append({
            'nombre': nombre,
            'apellido': apellido,
            'especialidad': especialidad,
            'cedula_profesional': cedula,
            'telefono': f'555-{random.randint(1000, 9999)}',
            'email': f'{nombre.lower()}.{apellido.lower()}{random.randint(1, 999)}@hospital.com',
            'fecha_contratacion': (datetime.now() - timedelta(days=random.randint(30, 3650))).strftime('%Y-%m-%d'),
            'salario': round(random.uniform(15000, 80000), 2),
            'activo': random.random() > 0.05
        })
    return doctors

def generate_appointments(count=3000, patients_count=1200, doctors_count=50):
    """Generar citas SIN campos id."""
    estados = ['Programada', 'Programada', 'Programada', 'Atendida', 'Cancelada', 'Reprogramada', 'No Asistió']
    motivos = ['Consulta general', 'Dolor de cabeza', 'Chequeo anual', 'Dolor abdominal', 'Seguimiento',
               'Dolor en el pecho', 'Mareos', 'Náuseas', 'Dolor muscular', 'Falta de aire',
               'Examen médico', 'Control de presión', 'Control de diabetes', 'Dolor de espalda', 'Problemas respiratorios',
               'Chequeo pediátrico', 'Control de embarazo', 'Problemas digestivos', 'Dolor articular', 'Problemas de piel']
    especialidades = ['Medicina General', 'Cardiología', 'Pediatría', 'Ginecología', 'Traumatología', 
                      'Neurología', 'Dermatología', 'Oftalmología', 'Otorrinolaringología', 'Urología',
                      'Psiquiatría', 'Reumatología', 'Endocrinología', 'Oncología', 'Neumología']
    
    appointments = []
    for i in range(count):
        fecha = datetime.now() + timedelta(days=random.randint(-90, 30), hours=random.randint(8, 18), minutes=random.randint(0, 59))
        appointments.append({
            'id_paciente': random.randint(1, patients_count),
            'id_medico': random.randint(1, doctors_count),
            'especialidad': random.choice(especialidades),
            'fecha_hora': fecha.isoformat(),
            'duracion': random.choice([15, 20, 25, 30, 45, 60]),
            'estado': random.choice(estados),
            'motivo': random.choice(motivos),
            'fecha_registro': (datetime.now() - timedelta(days=random.randint(0, 90))).isoformat()
        })
    return appointments

def generate_consultations(count=3000, patients_count=1200, doctors_count=50):
    """Generar consultas SIN campos id."""
    sintomas = ['Dolor de cabeza', 'Fiebre', 'Dolor abdominal', 'Tos persistente', 'Cansancio', 
                'Dolor en el pecho', 'Mareos', 'Náuseas', 'Dolor muscular', 'Falta de aire',
                'Dolor de garganta', 'Congestión nasal', 'Dolor de oído', 'Problemas digestivos', 'Dolor de espalda',
                'Erupciones en la piel', 'Picazón', 'Inflamación', 'Dolor articular', 'Sangrado']
    tipos = ['Primera vez', 'Seguimiento', 'Urgencia', 'Consulta de control']
    notas = ['Paciente en buen estado', 'Requiere seguimiento', 'Remitido a especialista', 'Sin observaciones',
             'Control de medicación', 'Exámenes solicitados', 'Cambio de tratamiento', 'Mejoría significativa',
             'Sin cambios', 'Empeoramiento de síntomas']
    especialidades = ['Medicina General', 'Cardiología', 'Pediatría', 'Ginecología', 'Traumatología', 
                      'Neurología', 'Dermatología', 'Oftalmología', 'Otorrinolaringología', 'Urología',
                      'Psiquiatría', 'Reumatología', 'Endocrinología', 'Oncología', 'Neumología']
    diagnostico_ingreso = ['Infección respiratoria', 'Gastritis', 'Hipertensión arterial', 'Diabetes', 'Artritis',
                          'Asma bronquial', 'Dermatitis', 'Conjuntivitis', 'Otitis', 'Cistitis']
    
    consultations = []
    for i in range(count):
        fecha = datetime.now() - timedelta(days=random.randint(0, 180), hours=random.randint(8, 18), minutes=random.randint(0, 59))
        consultations.append({
            'id_paciente': random.randint(1, patients_count),
            'id_medico': random.randint(1, doctors_count),
            'especialidad': random.choice(especialidades),
            'fecha_hora': fecha.isoformat(),
            'peso': round(random.uniform(45, 120), 1),
            'altura': round(random.uniform(140, 210), 1),
            'presion_arterial': f"{random.randint(100, 160)}/{random.randint(60, 100)}",
            'temperatura': round(random.uniform(35.5, 39.5), 1),
            'frecuencia_cardiaca': random.randint(50, 120),
            'sintomas': random.choice(sintomas),
            'notas_clinicas': random.choice(notas),
            'tipo_consulta': random.choice(tipos),
            'duracion_atencion': random.randint(10, 75),
            'diagnostico': random.choice(diagnostico_ingreso)
        })
    return consultations

def generate_hospitalizations(count=500, patients_count=1200, doctors_count=50):
    """Generar hospitalizaciones SIN campos id."""
    motivos = ['Dolor abdominal agudo', 'Dolor en el pecho', 'Fractura de fémur', 'Infección grave', 'Cirugía programada',
               'Neumonía', 'Accidente cerebrovascular', 'Infarto agudo al miocardio', 'Crisis de asma', 'Infección urinaria',
               'Pancreatitis', 'Apéndice', 'Colecistitis', 'Embarazo de alto riesgo', 'Quimioterapia']
    diagnosticos = ['Apendicitis', 'Angina de pecho', 'Fractura de fémur', 'Neumonía', 'Colecistitis',
                    'Diabetes descompensada', 'Hipertensión arterial', 'Infarto agudo al miocardio', 'Accidente cerebrovascular',
                    'Crisis asmática', 'Infección urinaria', 'Pancreatitis aguda', 'Embarazo ectópico', 'Cáncer de seno',
                    'Leucemia']
    estados = ['Activa', 'Alta', 'Traslado', 'Fallecimiento']
    tipos_ingreso = ['Programado', 'Urgencia']
    especialidades = ['Medicina General', 'Cardiología', 'Pediatría', 'Ginecología', 'Traumatología', 
                      'Neurología', 'Oncología', 'Neumología', 'Cirugía', 'Medicina Interna']
    
    hospitalizations = []
    for i in range(count):
        fecha_ingreso = datetime.now() - timedelta(days=random.randint(0, 180))
        estado = random.choice(estados)
        
        if estado == 'Alta' or estado == 'Fallecimiento':
            fecha_alta = fecha_ingreso + timedelta(days=random.randint(1, 30))
        else:
            fecha_alta = None
        
        hospitalizations.append({
            'id_paciente': random.randint(1, patients_count),
            'id_medico_responsable': random.randint(1, doctors_count),
            'fecha_ingreso': fecha_ingreso.isoformat(),
            'fecha_alta': fecha_alta.isoformat() if fecha_alta else None,
            'habitacion': f'{random.randint(1, 6)}0{random.randint(1, 9)}',
            'cama': random.choice(['A', 'B', 'C', 'D']),
            'motivo_ingreso': random.choice(motivos),
            'diagnostico_ingreso': random.choice(diagnosticos),
            'tipo_ingreso': random.choice(tipos_ingreso),
            'estado': estado,
            'observaciones': random.choice(['Paciente estable', 'En recuperación', 'Requiere cirugía', 'Observación', 
                                            'Mejoría gradual', 'Estable', 'Crítico', 'Favorable']),
            'especialidad': random.choice(especialidades),
            'dias_estancia': random.randint(1, 30)
        })
    return hospitalizations

def generate_medicines(count=200):
    """Generar medicamentos SIN campos id."""
    nombres = ['Paracetamol', 'Ibuprofeno', 'Amoxicilina', 'Loratadina', 'Omeprazol',
               'Acetaminofén', 'Naproxeno', 'Diclofenaco', 'Salbutamol', 'Metformina',
               'Losartán', 'Atorvastatina', 'Pantoprazol', 'Sertralina', 'Escitalopram',
               'Sinvastatina', 'Metoprolol', 'Enalapril', 'Furosemida', 'Diazepam',
               'Clonazepam', 'Alprazolam', 'Fluoxetina', 'Citalopram', 'Amlodipino',
               'Nifedipino', 'Carvedilol', 'Digoxina', 'Warfarina', 'Heparina',
               'Insulina', 'Levotiroxina', 'Prednisona', 'Dexametasona', 'Azitromicina',
               'Claritromicina', 'Ciprofloxacino', 'Levofloxacino', 'Metronidazol', 'Gabapentina']
    presentaciones = ['Tableta', 'Cápsula', 'Jarabe', 'Suspensión', 'Inyectable', 'Crema', 'Gotas', 'Parche', 'Polvo']
    laboratorios = ['Bayer', 'Pfizer', 'Roche', 'Novartis', 'AstraZeneca', 'GSK', 'Sanofi', 'Merck', 'Johnson & Johnson']
    proveedores = ['Distribuidora Médica', 'Farmacéutica Nacional', 'ImporMed', 'MediSupply', 'PharmaDist']
    
    medicines = []
    used_names = set()
    for i in range(count):
        nombre = random.choice(nombres)
        while nombre in used_names:
            nombre = f"{random.choice(nombres)} {random.choice(['Plus', 'Forte', 'Junior', 'Xtra', 'Dual'])}"
        used_names.add(nombre)
        
        medicines.append({
            'nombre': nombre,
            'principio_activo': random.choice([nombre, f'{nombre} Compuesto', f'{nombre} Plus']),
            'presentacion': random.choice(presentaciones),
            'concentracion': random.choice(['100mg', '200mg', '250mg', '500mg', '750mg', '1g', '10mg', '20mg', '50mg', '100mg/ml']),
            'precio_unitario': round(random.uniform(5, 500), 2),
            'stock': random.randint(0, 500),
            'stock_minimo': random.randint(5, 50),
            'requiere_receta': random.choice([True, False]),
            'fecha_caducidad': (datetime.now() + timedelta(days=random.randint(30, 730))).strftime('%Y-%m-%d'),
            'activo': True,
            'laboratorio': random.choice(laboratorios),
            'proveedor': random.choice(proveedores)
        })
    return medicines

def insert_data(db):
    """Insertar todos los datos en MongoDB."""
    
    print("\n" + "="*60)
    print("🚀 INSERTANDO MILES DE DATOS EN MONGODB")
    print("="*60)
    
    # ELIMINAR TODOS LOS ÍNDICES ANTES DE INSERTAR
    print("\n🗑️  Eliminando índices existentes...")
    collections = ['patients', 'doctors', 'appointments', 'consultations', 'hospitalizations', 'medicines']
    for coll_name in collections:
        if coll_name in db.list_collection_names():
            try:
                db[coll_name].drop_indexes()
                print(f"   ✅ Índices eliminados de {coll_name}")
            except Exception as e:
                print(f"   ℹ️ No se pudieron eliminar índices de {coll_name}: {e}")
    
    # 1. Especialidades
    specialties = [
        {'nombre': 'Medicina General', 'descripcion': 'Atención primaria y consultas generales', 'costo_consulta': 350, 'tiempo_promedio_atencion': 30, 'activo': True},
        {'nombre': 'Cardiología', 'descripcion': 'Diagnóstico y tratamiento de enfermedades del corazón', 'costo_consulta': 650, 'tiempo_promedio_atencion': 45, 'activo': True},
        {'nombre': 'Pediatría', 'descripcion': 'Atención médica para niños y adolescentes', 'costo_consulta': 400, 'tiempo_promedio_atencion': 30, 'activo': True},
        {'nombre': 'Ginecología', 'descripcion': 'Salud de la mujer y sistema reproductor', 'costo_consulta': 550, 'tiempo_promedio_atencion': 40, 'activo': True},
        {'nombre': 'Traumatología', 'descripcion': 'Lesiones del sistema musculoesquelético', 'costo_consulta': 500, 'tiempo_promedio_atencion': 35, 'activo': True},
        {'nombre': 'Neurología', 'descripcion': 'Trastornos del sistema nervioso', 'costo_consulta': 700, 'tiempo_promedio_atencion': 50, 'activo': True},
        {'nombre': 'Dermatología', 'descripcion': 'Enfermedades de la piel', 'costo_consulta': 450, 'tiempo_promedio_atencion': 30, 'activo': True},
        {'nombre': 'Oftalmología', 'descripcion': 'Cuidado de la vista y enfermedades oculares', 'costo_consulta': 500, 'tiempo_promedio_atencion': 35, 'activo': True},
        {'nombre': 'Otorrinolaringología', 'descripcion': 'Oído, nariz y garganta', 'costo_consulta': 480, 'tiempo_promedio_atencion': 35, 'activo': True},
        {'nombre': 'Urología', 'descripcion': 'Sistema urinario y masculino', 'costo_consulta': 550, 'tiempo_promedio_atencion': 40, 'activo': True},
    ]
    db.specialties.delete_many({})
    db.specialties.insert_many(specialties)
    print(f"✅ {len(specialties)} especialidades insertadas")
    
    # 2. Médicos
    print("\n📝 Generando médicos...")
    doctors = generate_doctors(50)
    db.doctors.delete_many({})
    db.doctors.insert_many(doctors)
    print(f"✅ {len(doctors)} médicos insertados")
    
    # 3. Pacientes
    print("\n📝 Generando pacientes...")
    patients = generate_patients(1200)
    db.patients.delete_many({})
    # Insertar en lotes de 100
    batch_size = 100
    for i in range(0, len(patients), batch_size):
        batch = patients[i:i+batch_size]
        db.patients.insert_many(batch)
        print(f"   Insertados {min(i+batch_size, len(patients))} de {len(patients)} pacientes")
    print(f"✅ {len(patients)} pacientes insertados")
    
    # 4. Medicamentos
    print("\n📝 Generando medicamentos...")
    medicines = generate_medicines(200)
    db.medicines.delete_many({})
    db.medicines.insert_many(medicines)
    print(f"✅ {len(medicines)} medicamentos insertados")
    
    # 5. Citas
    print("\n📝 Generando citas...")
    appointments = generate_appointments(3000, 1200, 50)
    db.appointments.delete_many({})
    for i in range(0, len(appointments), batch_size):
        batch = appointments[i:i+batch_size]
        db.appointments.insert_many(batch)
        print(f"   Insertadas {min(i+batch_size, len(appointments))} de {len(appointments)} citas")
    print(f"✅ {len(appointments)} citas insertadas")
    
    # 6. Consultas
    print("\n📝 Generando consultas...")
    consultations = generate_consultations(3000, 1200, 50)
    db.consultations.delete_many({})
    for i in range(0, len(consultations), batch_size):
        batch = consultations[i:i+batch_size]
        db.consultations.insert_many(batch)
        print(f"   Insertadas {min(i+batch_size, len(consultations))} de {len(consultations)} consultas")
    print(f"✅ {len(consultations)} consultas insertadas")
    
    # 7. Hospitalizaciones
    print("\n📝 Generando hospitalizaciones...")
    hospitalizations = generate_hospitalizations(500, 1200, 50)
    db.hospitalizations.delete_many({})
    db.hospitalizations.insert_many(hospitalizations)
    print(f"✅ {len(hospitalizations)} hospitalizaciones insertadas")
    
    # 8. Diagnósticos
    print("\n📝 Generando diagnósticos...")
    diagnostics = []
    codigos_cie10 = ['J06.9', 'K29.5', 'I10', 'E11.9', 'M06.9', 'J45.9', 'L20.9', 'H10.9', 'H66.9', 'N30.9']
    tipos_diag = ['Principal', 'Secundario', 'Comorbilidad']
    nombres_diag = ['Infección respiratoria aguda', 'Gastritis', 'Hipertensión arterial', 'Diabetes tipo 2', 
                    'Artritis reumatoide', 'Asma bronquial', 'Dermatitis atópica', 'Conjuntivitis aguda',
                    'Otitis media', 'Infección urinaria']
    
    consultas = list(db.consultations.find({}))
    for consulta in consultas[:1000]:
        diagnostics.append({
            'id_consulta': consulta['_id'],
            'codigo_cie10': random.choice(codigos_cie10),
            'nombre': random.choice(nombres_diag),
            'descripcion': random.choice(['Paciente con síntomas típicos', 'Diagnóstico confirmado por estudios', 
                                          'Requiere seguimiento', 'Condición crónica']),
            'tipo': random.choice(tipos_diag),
            'fecha_diagnostico': consulta['fecha_hora']
        })
    db.diagnostics.delete_many({})
    db.diagnostics.insert_many(diagnostics)
    print(f"✅ {len(diagnostics)} diagnósticos insertados")
    
    # 9. Tratamientos
    print("\n📝 Generando tratamientos...")
    treatments = []
    for consulta in consultas[:800]:
        treatments.append({
            'id_consulta': consulta['_id'],
            'id_medicamento': random.randint(1, 200),
            'dosis': random.choice(['1 tableta', '2 tabletas', '1 cápsula', '10 ml', '1 cucharada']),
            'frecuencia': random.choice(['Cada 8 horas', 'Cada 12 horas', 'Cada 24 horas', '3 veces al día', '2 veces al día']),
            'duracion_dias': random.randint(3, 30),
            'indicaciones': random.choice(['Tomar después de las comidas', 'Tomar en ayunas', 'Con abundante agua', 'Antes de dormir']),
            'fecha_inicio': consulta['fecha_hora'],
            'fecha_fin': (datetime.fromisoformat(consulta['fecha_hora']) + timedelta(days=random.randint(3, 30))).isoformat(),
            'activo': True
        })
    db.treatments.delete_many({})
    db.treatments.insert_many(treatments)
    print(f"✅ {len(treatments)} tratamientos insertados")
    
    # 10. Inventario
    print("\n📝 Generando movimientos de inventario...")
    inventory = []
    medicamentos = list(db.medicines.find({}))
    for medicamento in medicamentos[:100]:
        cantidad = random.randint(1, 100)
        inventory.append({
            'id_medicamento': medicamento['_id'],
            'tipo_movimiento': random.choice(['Entrada', 'Salida']),
            'cantidad': cantidad,
            'fecha': (datetime.now() - timedelta(days=random.randint(0, 90))).isoformat(),
            'responsable': random.choice(['Dr. García', 'Lic. Pérez', 'Enf. Martínez', 'Farmacéutica Díaz']),
            'observaciones': random.choice(['Compra regular', 'Donación', 'Transferencia', 'Devolución', 'Consumo'])    
        })
    db.inventory.delete_many({})
    db.inventory.insert_many(inventory)
    print(f"✅ {len(inventory)} movimientos de inventario insertados")
    
    # Mostrar resumen final
    print("\n" + "="*60)
    print("📊 RESUMEN FINAL DE DATOS")
    print("="*60)
    print(f"  - Especialidades: {db.specialties.count_documents({})}")
    print(f"  - Médicos: {db.doctors.count_documents({})}")
    print(f"  - Pacientes: {db.patients.count_documents({})}")
    print(f"  - Medicamentos: {db.medicines.count_documents({})}")
    print(f"  - Citas: {db.appointments.count_documents({})}")
    print(f"  - Consultas: {db.consultations.count_documents({})}")
    print(f"  - Hospitalizaciones: {db.hospitalizations.count_documents({})}")
    print(f"  - Diagnósticos: {db.diagnostics.count_documents({})}")
    print(f"  - Tratamientos: {db.treatments.count_documents({})}")
    print(f"  - Inventario: {db.inventory.count_documents({})}")
    
    print("\n" + "="*60)
    print("✅ DATOS INSERTADOS EXITOSAMENTE")
    print("="*60)

if __name__ == "__main__":
    db = get_mongo_connection()
    insert_data(db)
    print("\n🚀 Ahora ejecuta: python manage.py runserver")
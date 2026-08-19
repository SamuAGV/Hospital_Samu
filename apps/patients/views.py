from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import datetime
import pandas as pd

db = settings.MONGO_DB if hasattr(settings, 'MONGO_DB') else None

@login_required
def list_patients(request):
    """Listar todos los pacientes con paginación."""
    context = {
        'page_title': 'Pacientes',
    }
    
    if db is not None and settings.MONGO_CONNECTED:
        try:
            # Obtener todos los pacientes
            patients_cursor = db.patients.find({})
            patients_list = list(patients_cursor)
            
            # Convertir ObjectId a string
            for p in patients_list:
                p['id'] = str(p['_id'])
            
            # Paginación (20 pacientes por página)
            paginator = Paginator(patients_list, 20)
            page = request.GET.get('page', 1)
            
            try:
                patients = paginator.page(page)
            except PageNotAnInteger:
                patients = paginator.page(1)
            except EmptyPage:
                patients = paginator.page(paginator.num_pages)
            
            context['patients'] = patients
            context['total'] = len(patients_list)
            context['is_paginated'] = True
            context['paginator'] = paginator
            context['page_obj'] = patients
            
            # Estadísticas
            if patients_list:
                df = pd.DataFrame(patients_list)
                if 'genero' in df.columns:
                    context['mujeres'] = len(df[df['genero'] == 'Femenino'])
                    context['hombres'] = len(df[df['genero'] == 'Masculino'])
                    
        except Exception as e:
            messages.error(request, f'Error al cargar pacientes: {e}')
            context['patients'] = []
            context['total'] = 0
            context['is_paginated'] = False
    else:
        context['patients'] = []
        context['total'] = 0
        context['is_paginated'] = False
        context['mujeres'] = 0
        context['hombres'] = 0
    
    return render(request, 'patients/list.html', context)

@login_required
def search_patients(request):
    """Buscar pacientes con paginación."""
    query = request.GET.get('q', '')
    context = {
        'page_title': 'Buscar Pacientes',
        'query': query,
    }
    
    if query and db is not None and settings.MONGO_CONNECTED:
        try:
            patients_list = list(db.patients.find({
                '$or': [
                    {'nombre': {'$regex': query, '$options': 'i'}},
                    {'apellido': {'$regex': query, '$options': 'i'}},
                    {'telefono': {'$regex': query, '$options': 'i'}},
                    {'email': {'$regex': query, '$options': 'i'}}
                ]
            }))
            
            for p in patients_list:
                p['id'] = str(p['_id'])
            
            # Paginación
            paginator = Paginator(patients_list, 20)
            page = request.GET.get('page', 1)
            
            try:
                patients = paginator.page(page)
            except PageNotAnInteger:
                patients = paginator.page(1)
            except EmptyPage:
                patients = paginator.page(paginator.num_pages)
            
            context['patients'] = patients
            context['total'] = len(patients_list)
            context['is_paginated'] = True
            context['paginator'] = paginator
            context['page_obj'] = patients
            
        except Exception as e:
            messages.error(request, f'Error en la búsqueda: {e}')
            context['patients'] = []
            context['total'] = 0
            context['is_paginated'] = False
    else:
        context['patients'] = []
        context['total'] = 0
        context['is_paginated'] = False
    
    return render(request, 'patients/search.html', context)

# ... resto de funciones (create_patient, patient_detail, edit_patient, delete_patient) iguales
# ... (resto de las funciones igual pero con la variable db corregida)

@login_required
def create_patient(request):
    """Crear un nuevo paciente."""
    if request.method == 'POST':
        try:
            patient_data = {
                'nombre': request.POST.get('nombre'),
                'apellido': request.POST.get('apellido'),
                'fecha_nacimiento': request.POST.get('fecha_nacimiento'),
                'genero': request.POST.get('genero'),
                'telefono': request.POST.get('telefono'),
                'email': request.POST.get('email'),
                'direccion': request.POST.get('direccion'),
                'tipo_sangre': request.POST.get('tipo_sangre'),
                'alergias': request.POST.get('alergias'),
                'enfermedades_cronicas': request.POST.get('enfermedades_cronicas'),
                'fecha_registro': datetime.now().isoformat(),
                'activo': True
            }
            
            if db is not None:
                result = db.patients.insert_one(patient_data)
                messages.success(request, 'Paciente registrado correctamente')
                return redirect('patients:detail', patient_id=str(result.inserted_id))
            else:
                messages.warning(request, 'Base de datos no disponible, paciente no guardado')
                
        except Exception as e:
            messages.error(request, f'Error al registrar paciente: {e}')
    
    return render(request, 'patients/create.html')

@login_required
def patient_detail(request, patient_id):
    """Ver detalle de un paciente."""
    context = {'page_title': 'Detalle del Paciente'}
    
    if db is not None:
        try:
            from bson import ObjectId
            patient = db.patients.find_one({'_id': ObjectId(patient_id)})
            if patient:
                # Convertir ObjectId a string para el template
                patient['id'] = str(patient['_id'])
                context['patient'] = patient
                
                # Obtener historial de consultas
                consultations = list(db.consultations.find({'id_paciente': patient_id}))
                context['consultations'] = consultations
                
                # Obtener hospitalizaciones
                hospitalizations = list(db.hospitalizations.find({'id_paciente': patient_id}))
                context['hospitalizations'] = hospitalizations
            else:
                messages.error(request, 'Paciente no encontrado')
                return redirect('patients:list')
        except Exception as e:
            messages.error(request, f'Error al cargar paciente: {e}')
            return redirect('patients:list')
    
    return render(request, 'patients/detail.html', context)

@login_required
def edit_patient(request, patient_id):
    """Editar un paciente."""
    if request.method == 'POST':
        try:
            from bson import ObjectId
            update_data = {
                'nombre': request.POST.get('nombre'),
                'apellido': request.POST.get('apellido'),
                'fecha_nacimiento': request.POST.get('fecha_nacimiento'),
                'genero': request.POST.get('genero'),
                'telefono': request.POST.get('telefono'),
                'email': request.POST.get('email'),
                'direccion': request.POST.get('direccion'),
                'tipo_sangre': request.POST.get('tipo_sangre'),
                'alergias': request.POST.get('alergias'),
                'enfermedades_cronicas': request.POST.get('enfermedades_cronicas'),
            }
            
            if db is not None:
                result = db.patients.update_one(
                    {'_id': ObjectId(patient_id)},
                    {'$set': update_data}
                )
                if result.modified_count > 0:
                    messages.success(request, 'Paciente actualizado correctamente')
                else:
                    messages.warning(request, 'No se realizaron cambios')
                return redirect('patients:detail', patient_id=patient_id)
                
        except Exception as e:
            messages.error(request, f'Error al actualizar paciente: {e}')
    
    # GET: cargar datos del paciente
    context = {'page_title': 'Editar Paciente'}
    if db is not None:
        try:
            from bson import ObjectId
            patient = db.patients.find_one({'_id': ObjectId(patient_id)})
            if patient:
                patient['id'] = str(patient['_id'])
                context['patient'] = patient
            else:
                messages.error(request, 'Paciente no encontrado')
                return redirect('patients:list')
        except Exception as e:
            messages.error(request, f'Error al cargar paciente: {e}')
            return redirect('patients:list')
    
    return render(request, 'patients/edit.html', context)

@login_required
def delete_patient(request, patient_id):
    """Eliminar un paciente (desactivar)."""
    if request.method == 'POST':
        try:
            from bson import ObjectId
            if db is not None:
                result = db.patients.update_one(
                    {'_id': ObjectId(patient_id)},
                    {'$set': {'activo': False}}
                )
                if result.modified_count > 0:
                    messages.success(request, 'Paciente desactivado correctamente')
                else:
                    messages.warning(request, 'Paciente no encontrado')
        except Exception as e:
            messages.error(request, f'Error al eliminar paciente: {e}')
    
    return redirect('patients:list')

@login_required
def search_patients(request):
    """Buscar pacientes."""
    query = request.GET.get('q', '')
    context = {'page_title': 'Buscar Pacientes', 'query': query}
    
    if query and db is not None:
        try:
            patients = list(db.patients.find({
                '$or': [
                    {'nombre': {'$regex': query, '$options': 'i'}},
                    {'apellido': {'$regex': query, '$options': 'i'}},
                    {'telefono': {'$regex': query, '$options': 'i'}},
                    {'email': {'$regex': query, '$options': 'i'}}
                ]
            }))
            context['patients'] = patients
            context['total'] = len(patients)
        except Exception as e:
            messages.error(request, f'Error en la búsqueda: {e}')
    
    return render(request, 'patients/search.html', context)
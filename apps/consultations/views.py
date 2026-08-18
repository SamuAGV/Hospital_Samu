from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.conf import settings
from datetime import datetime
import pandas as pd

db = getattr(settings, 'mongo_db', None)

@login_required
def list_consultations(request):
    """Listar todas las consultas."""
    context = {'page_title': 'Consultas Médicas'}
    
    if db is not None:
        try:
            consultations = list(db.consultations.find({}, {'_id': 0}))
            context['consultations'] = consultations
            context['total'] = len(consultations)
            
            # Estadísticas
            if consultations:
                df = pd.DataFrame(consultations)
                if 'tipo_consulta' in df.columns:
                    context['tipos'] = df['tipo_consulta'].value_counts().to_dict()
        except Exception as e:
            messages.error(request, f'Error al cargar consultas: {e}')
            context['consultations'] = []
    
    return render(request, 'consultations/list.html', context)

@login_required
def create_consultation(request):
    """Crear una nueva consulta."""
    if request.method == 'POST':
        try:
            consultation_data = {
                'id_paciente': request.POST.get('id_paciente'),
                'id_medico': request.POST.get('id_medico'),
                'fecha_hora': datetime.now().isoformat(),
                'peso': float(request.POST.get('peso', 0)),
                'altura': float(request.POST.get('altura', 0)),
                'presion_arterial': request.POST.get('presion_arterial'),
                'temperatura': float(request.POST.get('temperatura', 0)),
                'frecuencia_cardiaca': int(request.POST.get('frecuencia_cardiaca', 0)),
                'sintomas': request.POST.get('sintomas'),
                'notas_clinicas': request.POST.get('notas_clinicas'),
                'tipo_consulta': request.POST.get('tipo_consulta', 'Consulta'),
                'duracion_atencion': int(request.POST.get('duracion_atencion', 30)),
            }
            
            if db is not None:
                db.consultations.insert_one(consultation_data)
                messages.success(request, 'Consulta registrada correctamente')
                return redirect('consultations:list')
                
        except Exception as e:
            messages.error(request, f'Error al registrar consulta: {e}')
    
    # Cargar pacientes y médicos para el formulario
    context = {'page_title': 'Nueva Consulta'}
    
    if db is not None:
        context['patients'] = list(db.patients.find({}, {'_id': 0}))
        context['doctors'] = list(db.doctors.find({}, {'_id': 0}))
    
    return render(request, 'consultations/create.html', context)

@login_required
def consultation_detail(request, consultation_id):
    """Ver detalle de una consulta."""
    context = {'page_title': 'Detalle de Consulta'}
    
    if db is not None:
        try:
            from bson import ObjectId
            consultation = db.consultations.find_one({'_id': ObjectId(consultation_id)})
            if consultation:
                consultation['id'] = str(consultation['_id'])
                context['consultation'] = consultation
                
                # Obtener diagnósticos asociados
                diagnostics = list(db.diagnostics.find({'id_consulta': consultation_id}))
                context['diagnostics'] = diagnostics
                
                # Obtener tratamientos asociados
                treatments = list(db.treatments.find({'id_consulta': consultation_id}))
                context['treatments'] = treatments
            else:
                messages.error(request, 'Consulta no encontrada')
                return redirect('consultations:list')
        except Exception as e:
            messages.error(request, f'Error al cargar consulta: {e}')
            return redirect('consultations:list')
    
    return render(request, 'consultations/detail.html', context)

@login_required
def edit_consultation(request, consultation_id):
    """Editar una consulta."""
    if request.method == 'POST':
        try:
            from bson import ObjectId
            update_data = {
                'peso': float(request.POST.get('peso', 0)),
                'altura': float(request.POST.get('altura', 0)),
                'presion_arterial': request.POST.get('presion_arterial'),
                'temperatura': float(request.POST.get('temperatura', 0)),
                'frecuencia_cardiaca': int(request.POST.get('frecuencia_cardiaca', 0)),
                'sintomas': request.POST.get('sintomas'),
                'notas_clinicas': request.POST.get('notas_clinicas'),
                'duracion_atencion': int(request.POST.get('duracion_atencion', 30)),
            }
            
            if db is not None:
                db.consultations.update_one(
                    {'_id': ObjectId(consultation_id)},
                    {'$set': update_data}
                )
                messages.success(request, 'Consulta actualizada correctamente')
                return redirect('consultations:detail', consultation_id=consultation_id)
                
        except Exception as e:
            messages.error(request, f'Error al actualizar consulta: {e}')
    
    # GET: cargar datos
    context = {'page_title': 'Editar Consulta'}
    if db is not None:
        try:
            from bson import ObjectId
            consultation = db.consultations.find_one({'_id': ObjectId(consultation_id)})
            if consultation:
                consultation['id'] = str(consultation['_id'])
                context['consultation'] = consultation
        except Exception as e:
            messages.error(request, f'Error al cargar consulta: {e}')
            return redirect('consultations:list')
    
    return render(request, 'consultations/edit.html', context)

@login_required
def add_diagnostic(request, consultation_id):
    """Agregar diagnóstico a una consulta."""
    if request.method == 'POST':
        try:
            diagnostic_data = {
                'id_consulta': consultation_id,
                'codigo_cie10': request.POST.get('codigo_cie10'),
                'nombre': request.POST.get('nombre'),
                'descripcion': request.POST.get('descripcion'),
                'tipo': request.POST.get('tipo', 'Principal'),
                'fecha_diagnostico': datetime.now().isoformat()
            }
            
            if db is not None:
                db.diagnostics.insert_one(diagnostic_data)
                messages.success(request, 'Diagnóstico agregado correctamente')
                
        except Exception as e:
            messages.error(request, f'Error al agregar diagnóstico: {e}')
    
    return redirect('consultations:detail', consultation_id=consultation_id)

@login_required
def add_treatment(request, consultation_id):
    """Agregar tratamiento a una consulta."""
    if request.method == 'POST':
        try:
            treatment_data = {
                'id_consulta': consultation_id,
                'id_medicamento': request.POST.get('id_medicamento'),
                'dosis': request.POST.get('dosis'),
                'frecuencia': request.POST.get('frecuencia'),
                'duracion_dias': int(request.POST.get('duracion_dias', 0)),
                'indicaciones': request.POST.get('indicaciones'),
                'fecha_inicio': datetime.now().isoformat(),
                'activo': True
            }
            
            if db is not None:
                db.treatments.insert_one(treatment_data)
                messages.success(request, 'Tratamiento agregado correctamente')
                
        except Exception as e:
            messages.error(request, f'Error al agregar tratamiento: {e}')
    
    return redirect('consultations:detail', consultation_id=consultation_id)

@login_required
def consultation_stats(request):
    """Estadísticas de consultas."""
    context = {'page_title': 'Estadísticas de Consultas'}
    
    if db is not None:
        try:
            # Consultas por tipo
            pipeline_tipo = [
                {'$group': {'_id': '$tipo_consulta', 'count': {'$sum': 1}}}
            ]
            context['por_tipo'] = list(db.consultations.aggregate(pipeline_tipo))
            
            # Consultas por especialidad
            pipeline_esp = [
                {'$group': {'_id': '$especialidad', 'count': {'$sum': 1}}},
                {'$sort': {'count': -1}}
            ]
            context['por_especialidad'] = list(db.consultations.aggregate(pipeline_esp))
            
            # Promedio de duración
            pipeline_prom = [
                {'$group': {'_id': None, 'avg_duracion': {'$avg': '$duracion_atencion'}}}
            ]
            result = list(db.consultations.aggregate(pipeline_prom))
            context['avg_duracion'] = result[0]['avg_duracion'] if result else 0
            
        except Exception as e:
            messages.error(request, f'Error al obtener estadísticas: {e}')
    
    return render(request, 'consultations/stats.html', context)
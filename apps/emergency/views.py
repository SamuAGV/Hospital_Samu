from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import datetime
import pandas as pd

db = settings.MONGO_DB if hasattr(settings, 'MONGO_DB') else None

@login_required
def dashboard(request):
    """Dashboard de urgencias."""
    context = {'page_title': 'Urgencias'}
    
    if db is not None and settings.MONGO_CONNECTED:
        try:
            emergencies_cursor = db.emergencies.find({})
            emergencies_list = list(emergencies_cursor)
            
            for e in emergencies_list:
                e['id'] = str(e['_id'])
            
            # Paginación
            paginator = Paginator(emergencies_list, 20)
            page = request.GET.get('page', 1)
            
            try:
                emergencies = paginator.page(page)
            except PageNotAnInteger:
                emergencies = paginator.page(1)
            except EmptyPage:
                emergencies = paginator.page(paginator.num_pages)
            
            context['emergencies'] = emergencies
            context['total'] = len(emergencies_list)
            context['is_paginated'] = True
            context['paginator'] = paginator
            context['page_obj'] = emergencies
            
            # Prioridades
            priorities = db.emergencies.aggregate([
                {'$group': {'_id': '$prioridad', 'count': {'$sum': 1}}}
            ])
            context['priorities'] = {p['_id']: p['count'] for p in priorities}
            
            # Tiempo promedio de espera (simulado)
            context['avg_wait_time'] = 15
            
        except Exception as e:
            messages.error(request, f'Error al cargar urgencias: {e}')
            context['emergencies'] = []
            context['total'] = 0
            context['priorities'] = {}
            context['is_paginated'] = False
    else:
        context['emergencies'] = []
        context['total'] = 0
        context['priorities'] = {}
        context['is_paginated'] = False
    
    return render(request, 'emergency/dashboard.html', context)

@login_required
def register_patient(request):
    """Registrar paciente en urgencias."""
    if request.method == 'POST':
        try:
            emergency_data = {
                'id_paciente': request.POST.get('id_paciente'),
                'fecha_hora_ingreso': datetime.now().isoformat(),
                'prioridad': request.POST.get('prioridad', 'Media'),
                'sintomas': request.POST.get('sintomas'),
                'presion_arterial': request.POST.get('presion_arterial'),
                'frecuencia_cardiaca': int(request.POST.get('frecuencia_cardiaca', 0)),
                'temperatura': float(request.POST.get('temperatura', 0)),
                'notas': request.POST.get('notas'),
                'estado': 'En espera'
            }
            
            if db is not None and settings.MONGO_CONNECTED:
                db.emergencies.insert_one(emergency_data)
                messages.success(request, 'Paciente registrado en urgencias')
                return redirect('emergency:dashboard')
                
        except Exception as e:
            messages.error(request, f'Error al registrar: {e}')
    
    context = {'page_title': 'Registrar en Urgencias'}
    if db is not None and settings.MONGO_CONNECTED:
        context['patients'] = list(db.patients.find({}))
    
    return render(request, 'emergency/register.html', context)

@login_required
def emergency_detail(request, emergency_id):
    """Ver detalle de urgencia."""
    context = {'page_title': 'Detalle de Urgencia'}
    
    if db is not None and settings.MONGO_CONNECTED:
        try:
            from bson import ObjectId
            emergency = db.emergencies.find_one({'_id': ObjectId(emergency_id)})
            if emergency:
                emergency['id'] = str(emergency['_id'])
                context['emergency'] = emergency
            else:
                messages.error(request, 'Registro no encontrado')
                return redirect('emergency:dashboard')
        except Exception as e:
            messages.error(request, f'Error al cargar: {e}')
            return redirect('emergency:dashboard')
    
    return render(request, 'emergency/detail.html', context)

@login_required
def emergency_stats(request):
    """Estadísticas de urgencias."""
    context = {'page_title': 'Estadísticas de Urgencias'}
    
    if db is not None and settings.MONGO_CONNECTED:
        try:
            # Por prioridad
            pipeline = [
                {'$group': {'_id': '$prioridad', 'count': {'$sum': 1}}}
            ]
            context['por_prioridad'] = list(db.emergencies.aggregate(pipeline))
            context['total'] = db.emergencies.count_documents({})
            
            # Por hora
            pipeline_hora = [
                {'$group': {'_id': {'$hour': '$fecha_hora_ingreso'}, 'count': {'$sum': 1}}},
                {'$sort': {'_id': 1}}
            ]
            context['por_hora'] = list(db.emergencies.aggregate(pipeline_hora))
            
        except Exception as e:
            messages.error(request, f'Error al obtener estadísticas: {e}')
    
    return render(request, 'emergency/stats.html', context)
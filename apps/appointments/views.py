from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import datetime, timedelta
import pandas as pd

db = settings.MONGO_DB if hasattr(settings, 'MONGO_DB') else None

@login_required
def list_appointments(request):
    """Listar citas con paginación."""
    context = {'page_title': 'Citas Médicas'}
    
    if db is not None and settings.MONGO_CONNECTED:
        try:
            appointments_cursor = db.appointments.find({})
            appointments_list = list(appointments_cursor)
            
            for app in appointments_list:
                app['id'] = str(app['_id'])
            
            paginator = Paginator(appointments_list, 20)
            page = request.GET.get('page', 1)
            
            try:
                appointments = paginator.page(page)
            except PageNotAnInteger:
                appointments = paginator.page(1)
            except EmptyPage:
                appointments = paginator.page(paginator.num_pages)
            
            context['appointments'] = appointments
            context['total'] = len(appointments_list)
            context['is_paginated'] = True
            context['paginator'] = paginator
            context['page_obj'] = appointments
            
            status_counts = db.appointments.aggregate([
                {'$group': {'_id': '$estado', 'count': {'$sum': 1}}}
            ])
            context['status_stats'] = {s['_id']: s['count'] for s in status_counts}
            
        except Exception as e:
            messages.error(request, f'Error al cargar citas: {e}')
            context['appointments'] = []
            context['total'] = 0
            context['is_paginated'] = False
            context['status_stats'] = {}
    else:
        context['appointments'] = []
        context['total'] = 0
        context['is_paginated'] = False
        context['status_stats'] = {}
    
    return render(request, 'appointments/list.html', context)

@login_required
def create_appointment(request):
    """Crear una cita."""
    if request.method == 'POST':
        try:
            appointment_data = {
                'id_paciente': request.POST.get('id_paciente'),
                'id_medico': request.POST.get('id_medico'),
                'fecha_hora': request.POST.get('fecha_hora'),
                'duracion': int(request.POST.get('duracion', 30)),
                'estado': 'Programada',
                'motivo': request.POST.get('motivo'),
                'fecha_registro': datetime.now().isoformat(),
            }
            
            if db is not None and settings.MONGO_CONNECTED:
                db.appointments.insert_one(appointment_data)
                messages.success(request, 'Cita agendada correctamente')
                return redirect('appointments:list')
                
        except Exception as e:
            messages.error(request, f'Error al agendar cita: {e}')
    
    context = {'page_title': 'Agendar Cita'}
    if db is not None and settings.MONGO_CONNECTED:
        context['patients'] = list(db.patients.find({}))
        context['doctors'] = list(db.doctors.find({}))
    
    return render(request, 'appointments/create.html', context)

@login_required
def appointment_detail(request, appointment_id):
    """Ver detalle de una cita."""
    context = {'page_title': 'Detalle de Cita'}
    
    if db is not None and settings.MONGO_CONNECTED:
        try:
            from bson import ObjectId
            appointment = db.appointments.find_one({'_id': ObjectId(appointment_id)})
            if appointment:
                appointment['id'] = str(appointment['_id'])
                context['appointment'] = appointment
            else:
                messages.error(request, 'Cita no encontrada')
                return redirect('appointments:list')
        except Exception as e:
            messages.error(request, f'Error al cargar cita: {e}')
            return redirect('appointments:list')
    
    return render(request, 'appointments/detail.html', context)

@login_required
def cancel_appointment(request, appointment_id):
    """Cancelar una cita."""
    if request.method == 'POST':
        try:
            from bson import ObjectId
            motivo = request.POST.get('motivo', 'Cancelada por el usuario')
            
            if db is not None and settings.MONGO_CONNECTED:
                result = db.appointments.update_one(
                    {'_id': ObjectId(appointment_id)},
                    {
                        '$set': {
                            'estado': 'Cancelada',
                            'fecha_cancelacion': datetime.now().isoformat(),
                            'motivo_cancelacion': motivo
                        }
                    }
                )
                if result.modified_count > 0:
                    messages.success(request, 'Cita cancelada correctamente')
                else:
                    messages.warning(request, 'No se pudo cancelar la cita')
                    
        except Exception as e:
            messages.error(request, f'Error al cancelar cita: {e}')
    
    return redirect('appointments:list')

@login_required
def reschedule_appointment(request, appointment_id):
    """Reagendar una cita."""
    if request.method == 'POST':
        try:
            from bson import ObjectId
            nueva_fecha = request.POST.get('nueva_fecha_hora')
            motivo = request.POST.get('motivo', 'Reagendada por el usuario')
            
            if db is not None and settings.MONGO_CONNECTED:
                result = db.appointments.update_one(
                    {'_id': ObjectId(appointment_id)},
                    {
                        '$set': {
                            'fecha_hora': nueva_fecha,
                            'estado': 'Reprogramada',
                            'motivo_reagendamiento': motivo
                        }
                    }
                )
                if result.modified_count > 0:
                    messages.success(request, 'Cita reagendada correctamente')
                else:
                    messages.warning(request, 'No se pudo reagendar la cita')
                    
        except Exception as e:
            messages.error(request, f'Error al reagendar cita: {e}')
    
    return redirect('appointments:list')

@login_required
def check_availability(request):
    """Verificar disponibilidad de citas."""
    fecha = request.GET.get('fecha')
    especialidad = request.GET.get('especialidad')
    
    if db is not None and settings.MONGO_CONNECTED:
        try:
            query = {'fecha_hora': {'$regex': f'^{fecha}'}}
            if especialidad:
                query['especialidad'] = especialidad
            
            count = db.appointments.count_documents(query)
            
            return JsonResponse({
                'available': count < 20,
                'count': count,
                'limit': 20,
                'message': f'Hay {count} citas agendadas para esa fecha'
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Base de datos no disponible'}, status=503)
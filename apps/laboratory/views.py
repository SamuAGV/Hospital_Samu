from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from datetime import datetime

db = getattr(settings, 'mongo_db', None)

@login_required
def dashboard(request):
    """Dashboard de laboratorio."""
    context = {'page_title': 'Laboratorio'}
    
    if db is not None:
        try:
            requests = list(db.lab_requests.find({}, {'_id': 0}))
            context['requests'] = requests
            context['total'] = len(requests)
            
            # Por estado
            status_counts = db.lab_requests.aggregate([
                {'$group': {'_id': '$estado', 'count': {'$sum': 1}}}
            ])
            context['status_counts'] = {s['_id']: s['count'] for s in status_counts}
            
        except Exception as e:
            messages.error(request, f'Error al cargar laboratorio: {e}')
            context['requests'] = []
    
    return render(request, 'laboratory/dashboard.html', context)

@login_required
def create_request(request):
    """Crear solicitud de laboratorio."""
    if request.method == 'POST':
        try:
            request_data = {
                'id_paciente': request.POST.get('id_paciente'),
                'id_medico': request.POST.get('id_medico'),
                'nombre_estudio': request.POST.get('nombre_estudio'),
                'tipo_estudio': request.POST.get('tipo_estudio'),
                'fecha_solicitud': datetime.now().isoformat(),
                'estado': 'Solicitado',
                'observaciones': request.POST.get('observaciones')
            }
            
            if db is not None:
                db.lab_requests.insert_one(request_data)
                messages.success(request, 'Solicitud de laboratorio registrada')
                return redirect('laboratory:dashboard')
                
        except Exception as e:
            messages.error(request, f'Error al registrar solicitud: {e}')
    
    context = {'page_title': 'Nueva Solicitud de Laboratorio'}
    if db is not None:
        context['patients'] = list(db.patients.find({}, {'_id': 0}))
        context['doctors'] = list(db.doctors.find({}, {'_id': 0}))
    
    return render(request, 'laboratory/create_request.html', context)

@login_required
def request_detail(request, request_id):
    """Ver detalle de solicitud."""
    context = {'page_title': 'Detalle de Solicitud'}
    
    if db is not None:
        try:
            from bson import ObjectId
            lab_request = db.lab_requests.find_one({'_id': ObjectId(request_id)})
            if lab_request:
                lab_request['id'] = str(lab_request['_id'])
                context['request'] = lab_request
            else:
                messages.error(request, 'Solicitud no encontrada')
                return redirect('laboratory:dashboard')
        except Exception as e:
            messages.error(request, f'Error al cargar: {e}')
            return redirect('laboratory:dashboard')
    
    return render(request, 'laboratory/request_detail.html', context)

@login_required
def add_result(request, request_id):
    """Agregar resultado a una solicitud."""
    if request.method == 'POST':
        try:
            from bson import ObjectId
            update_data = {
                'resultado': request.POST.get('resultado'),
                'fecha_resultado': datetime.now().isoformat(),
                'estado': 'Completado'
            }
            
            if db is not None:
                db.lab_requests.update_one(
                    {'_id': ObjectId(request_id)},
                    {'$set': update_data}
                )
                messages.success(request, 'Resultado registrado correctamente')
                
        except Exception as e:
            messages.error(request, f'Error al registrar resultado: {e}')
    
    return redirect('laboratory:request_detail', request_id=request_id)

@login_required
def lab_stats(request):
    """Estadísticas de laboratorio."""
    context = {'page_title': 'Estadísticas de Laboratorio'}
    
    if db is not None:
        try:
            # Por tipo de estudio
            pipeline = [
                {'$group': {'_id': '$tipo_estudio', 'count': {'$sum': 1}}}
            ]
            context['por_tipo'] = list(db.lab_requests.aggregate(pipeline))
            
            # Por estado
            pipeline_estado = [
                {'$group': {'_id': '$estado', 'count': {'$sum': 1}}}
            ]
            context['por_estado'] = list(db.lab_requests.aggregate(pipeline_estado))
            
        except Exception as e:
            messages.error(request, f'Error al obtener estadísticas: {e}')
    
    return render(request, 'laboratory/stats.html', context)
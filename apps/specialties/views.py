from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings

db = settings.MONGO_DB if hasattr(settings, 'MONGO_DB') else None

@login_required
def list_specialties(request):
    """Listar especialidades."""
    context = {'page_title': 'Especialidades Médicas'}
    
    if db is not None and settings.MONGO_CONNECTED:
        try:
            specialties = list(db.specialties.find({}))
            context['specialties'] = specialties
            
            # Obtener estadísticas de consultas por especialidad
            pipeline = [
                {'$group': {'_id': '$especialidad', 'total': {'$sum': 1}}},
                {'$sort': {'total': -1}}
            ]
            stats_list = list(db.consultations.aggregate(pipeline))
            
            stats_dict = {}
            for item in stats_list:
                if item['_id']:
                    stats_dict[item['_id']] = item['total']
            context['stats'] = stats_dict
            
        except Exception as e:
            messages.error(request, f'Error al cargar especialidades: {e}')
            context['specialties'] = []
            context['stats'] = {}
    else:
        context['specialties'] = []
        context['stats'] = {}
    
    return render(request, 'specialties/list.html', context)

# ... (resto de las funciones igual pero con la variable db corregida)
@login_required
def create_specialty(request):
    """Crear nueva especialidad."""
    if request.method == 'POST':
        try:
            specialty_data = {
                'nombre': request.POST.get('nombre'),
                'descripcion': request.POST.get('descripcion'),
                'costo_consulta': float(request.POST.get('costo_consulta', 0)),
                'tiempo_promedio_atencion': int(request.POST.get('tiempo_promedio', 30)),
                'activo': True
            }
            
            if db is not None:
                db.specialties.insert_one(specialty_data)
                messages.success(request, 'Especialidad creada correctamente')
                return redirect('specialties:list')
        except Exception as e:
            messages.error(request, f'Error al crear especialidad: {e}')
    
    return render(request, 'specialties/create.html')
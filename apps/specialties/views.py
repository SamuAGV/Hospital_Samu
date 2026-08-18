from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings

db = getattr(settings, 'mongo_db', None)

@login_required
def list_specialties(request):
    """Listar especialidades."""
    context = {'page_title': 'Especialidades Médicas'}
    
    if db is not None:
        try:
            specialties = list(db.specialties.find({}, {'_id': 0}))
            context['specialties'] = specialties
            
            # Obtener estadísticas de consultas por especialidad
            pipeline = [
                {'$group': {'_id': '$especialidad', 'total': {'$sum': 1}}},
                {'$sort': {'total': -1}}
            ]
            stats_list = list(db.consultations.aggregate(pipeline))
            
            # Convertir a diccionario para fácil acceso
            stats_dict = {}
            for item in stats_list:
                if item['_id']:  # Si la especialidad no es None
                    stats_dict[item['_id']] = item['total']
            
            context['stats'] = stats_dict
            
        except Exception as e:
            messages.error(request, f'Error al cargar especialidades: {e}')
            context['specialties'] = []
            context['stats'] = {}
    else:
        # Datos de ejemplo
        context['specialties'] = [
            {'id_especialidad': 1, 'nombre': 'Medicina General', 'descripcion': 'Atención primaria', 'costo_consulta': 350},
            {'id_especialidad': 2, 'nombre': 'Cardiología', 'descripcion': 'Enfermedades del corazón', 'costo_consulta': 650},
            {'id_especialidad': 3, 'nombre': 'Pediatría', 'descripcion': 'Atención infantil', 'costo_consulta': 400},
        ]
        context['stats'] = {}
    
    return render(request, 'specialties/list.html', context)

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
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.conf import settings
from datetime import datetime

db = getattr(settings, 'mongo_db', None)

@login_required
def list_hospitalizations(request):
    """Listar hospitalizaciones."""
    context = {'page_title': 'Hospitalizaciones'}
    
    if db is not None:
        try:
            hospitalizations = list(db.hospitalizations.find({}))
            # Convertir ObjectId a string para los templates
            for h in hospitalizations:
                h['id'] = str(h['_id'])
            context['hospitalizations'] = hospitalizations
            context['total'] = len(hospitalizations)
            
            # Pacientes activos
            active = db.hospitalizations.count_documents({'estado': 'Activa'})
            context['active'] = active
            
        except Exception as e:
            messages.error(request, f'Error al cargar hospitalizaciones: {e}')
            context['hospitalizations'] = []
    else:
        context['hospitalizations'] = []
        context['total'] = 0
        context['active'] = 0
    
    return render(request, 'hospitalizations/list.html', context)

@login_required
def create_hospitalization(request):
    """Crear una hospitalización."""
    if request.method == 'POST':
        try:
            hospitalization_data = {
                'id_paciente': request.POST.get('id_paciente'),
                'id_medico_responsable': request.POST.get('id_medico_responsable'),
                'fecha_ingreso': datetime.now().isoformat(),
                'habitacion': request.POST.get('habitacion'),
                'cama': request.POST.get('cama'),
                'motivo_ingreso': request.POST.get('motivo_ingreso'),
                'diagnostico_ingreso': request.POST.get('diagnostico_ingreso'),
                'tipo_ingreso': request.POST.get('tipo_ingreso', 'Programado'),
                'estado': 'Activa',
                'observaciones': request.POST.get('observaciones')
            }
            
            if db is not None:
                db.hospitalizations.insert_one(hospitalization_data)
                messages.success(request, 'Paciente hospitalizado correctamente')
                return redirect('hospitalizations:list')
                
        except Exception as e:
            messages.error(request, f'Error al hospitalizar paciente: {e}')
    
    # GET: Cargar datos para el formulario
    context = {'page_title': 'Hospitalizar Paciente'}
    if db is not None:
        try:
            context['patients'] = list(db.patients.find({}))
            context['doctors'] = list(db.doctors.find({}))
        except Exception as e:
            messages.error(request, f'Error al cargar datos: {e}')
            context['patients'] = []
            context['doctors'] = []
    
    return render(request, 'hospitalizations/create.html', context)

@login_required
def hospitalization_detail(request, hospitalization_id):
    """Ver detalle de hospitalización."""
    context = {'page_title': 'Detalle de Hospitalización'}
    
    if db is not None:
        try:
            from bson import ObjectId
            hospitalization = db.hospitalizations.find_one({'_id': ObjectId(hospitalization_id)})
            if hospitalization:
                hospitalization['id'] = str(hospitalization['_id'])
                context['hospitalization'] = hospitalization
            else:
                messages.error(request, 'Hospitalización no encontrada')
                return redirect('hospitalizations:list')
        except Exception as e:
            messages.error(request, f'Error al cargar hospitalización: {e}')
            return redirect('hospitalizations:list')
    
    return render(request, 'hospitalizations/detail.html', context)

@login_required
def discharge_patient(request, hospitalization_id):
    """Dar de alta a un paciente."""
    if request.method == 'POST':
        try:
            from bson import ObjectId
            update_data = {
                'fecha_alta': datetime.now().isoformat(),
                'estado': 'Alta',
                'observaciones': request.POST.get('observaciones', 'Alta médica')
            }
            
            if db is not None:
                db.hospitalizations.update_one(
                    {'_id': ObjectId(hospitalization_id)},
                    {'$set': update_data}
                )
                messages.success(request, 'Paciente dado de alta correctamente')
                
        except Exception as e:
            messages.error(request, f'Error al dar de alta: {e}')
    
    return redirect('hospitalizations:list')

@login_required
def occupancy_view(request):
    """Ver ocupación hospitalaria."""
    context = {'page_title': 'Ocupación Hospitalaria'}
    
    if db is not None:
        try:
            total_camas = 120  # Configurable
            ocupadas = db.hospitalizations.count_documents({'estado': 'Activa'})
            
            context['total_camas'] = total_camas
            context['camas_ocupadas'] = ocupadas
            context['porcentaje'] = round((ocupadas / total_camas) * 100, 1)
            
            # Ocupación por área (simulada)
            context['areas'] = [
                {'area': 'Medicina Interna', 'ocupadas': 25, 'total': 30, 'porcentaje': 83},
                {'area': 'Cardiología', 'ocupadas': 18, 'total': 20, 'porcentaje': 90},
                {'area': 'Cirugía', 'ocupadas': 12, 'total': 20, 'porcentaje': 60},
                {'area': 'Pediatría', 'ocupadas': 10, 'total': 15, 'porcentaje': 67},
                {'area': 'Ginecología', 'ocupadas': 8, 'total': 15, 'porcentaje': 53},
                {'area': 'Traumatología', 'ocupadas': 7, 'total': 10, 'porcentaje': 70},
                {'area': 'Urgencias', 'ocupadas': 10, 'total': 10, 'porcentaje': 100},
            ]
            
        except Exception as e:
            messages.error(request, f'Error al obtener ocupación: {e}')
    
    return render(request, 'hospitalizations/occupancy.html', context)
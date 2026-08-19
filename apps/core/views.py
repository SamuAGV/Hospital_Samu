from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings
from datetime import datetime, timedelta
import json
from collections import defaultdict

db = settings.MONGO_DB if hasattr(settings, 'MONGO_DB') else None

@login_required(login_url='/users/login/')
def dashboard(request):
    """Vista principal del dashboard."""
    
    context = {
        'page_title': 'Dashboard General',
        'user': request.user,
        'current_date': datetime.now().strftime('%d/%m/%Y %H:%M'),
    }
    
    if db is not None and settings.MONGO_CONNECTED:
        try:
            # Métricas
            context['patients_count'] = db.patients.count_documents({})
            context['consultations_count'] = db.consultations.count_documents({})
            context['appointments_count'] = db.appointments.count_documents({'estado': 'Programada'})
            context['active_hospitalizations'] = db.hospitalizations.count_documents({'estado': 'Activa'})
            
            total_camas = 120
            context['occupancy_percent'] = round((context['active_hospitalizations'] / total_camas) * 100, 1) if total_camas > 0 else 0
            
            # Obtener datos de demanda
            demand_data = get_demand_data_simple()
            context['demand_data'] = json.dumps(demand_data)
            
            print(f"📊 Dashboard cargado:")
            print(f"  - Pacientes: {context['patients_count']}")
            print(f"  - Consultas: {context['consultations_count']}")
            print(f"  - Citas: {context['appointments_count']}")
            print(f"  - Hospitalizados: {context['active_hospitalizations']}")
            print(f"  - Días con datos: {len(demand_data.get('dates', []))}")
            
        except Exception as e:
            print(f"❌ Error en dashboard: {e}")
            context['demand_data'] = json.dumps({'dates': [], 'values': []})
    else:
        context['demand_data'] = json.dumps({'dates': [], 'values': []})
    
    return render(request, 'core/dashboard.html', context)

def get_demand_data_simple():
    """Obtener datos de demanda en formato simple."""
    if db is None:
        return {'dates': [], 'values': []}
    
    try:
        today = datetime.now()
        start_date = today - timedelta(days=90)
        
        consultations = list(db.consultations.find({
            'fecha_hora': {'$gte': start_date.isoformat()}
        }))
        
        if len(consultations) == 0:
            return {'dates': [], 'values': []}
        
        daily_counts = defaultdict(int)
        for consulta in consultations:
            fecha_hora = consulta.get('fecha_hora')
            if fecha_hora:
                try:
                    if isinstance(fecha_hora, str):
                        fecha = fecha_hora[:10]
                    else:
                        fecha = str(fecha_hora)[:10]
                    daily_counts[fecha] += 1
                except:
                    pass
        
        if not daily_counts:
            return {'dates': [], 'values': []}
        
        dates = sorted(daily_counts.keys())
        values = [daily_counts[d] for d in dates]
        
        return {'dates': dates, 'values': values}
        
    except Exception as e:
        print(f"❌ Error en get_demand_data: {e}")
        return {'dates': [], 'values': []}
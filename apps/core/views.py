from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import JsonResponse
from datetime import datetime, timedelta
import plotly.graph_objs as go
import plotly.utils
import json
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

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
            
            # OBTENER DATOS EN FORMATO SIMPLE
            demand_data = get_demand_data_simple()
            context['demand_data'] = json.dumps(demand_data)
            
        except Exception as e:
            print(f"❌ Error en dashboard: {e}")
            context['demand_data'] = json.dumps({'dates': [], 'values': []})
    else:
        context['demand_data'] = json.dumps({'dates': [], 'values': []})
    
    return render(request, 'core/dashboard.html', context)

def get_demand_data_simple():
    """Obtener datos de demanda en formato simple (dict)."""
    if db is None:
        return {'dates': [], 'values': []}
    
    try:
        today = datetime.now()
        start_date = today - timedelta(days=90)
        
        print(f"🔍 Buscando consultas desde: {start_date.isoformat()}")
        
        # Obtener consultas
        consultations = list(db.consultations.find({
            'fecha_hora': {'$gte': start_date.isoformat()}
        }))
        
        print(f"📊 Consultas encontradas: {len(consultations)}")
        
        if len(consultations) == 0:
            return {'dates': [], 'values': []}
        
        # Agrupar por fecha
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
        
        # Ordenar
        dates = sorted(daily_counts.keys())
        values = [daily_counts[d] for d in dates]
        
        print(f"📈 Días con datos: {len(dates)}")
        print(f"📊 Total: {sum(values)}")
        print(f"📅 Rango: {dates[0]} hasta {dates[-1]}")
        
        return {
            'dates': dates,
            'values': values
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return {'dates': [], 'values': []}
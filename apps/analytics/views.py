from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import json
import plotly.graph_objs as go
import plotly.utils
from collections import defaultdict

db = settings.MONGO_DB if hasattr(settings, 'MONGO_DB') else None

@login_required
def dashboard(request):
    """Dashboard de análisis."""
    context = {'page_title': 'Análisis Hospitalario'}
    
    if db is not None and settings.MONGO_CONNECTED:
        try:
            context['heatmap_data'] = get_heatmap_data()
            context['demand_data'] = get_demand_data()
            context['forecast_data'] = get_forecast_data()
        except Exception as e:
            context['error'] = str(e)
    else:
        context['error'] = 'No hay conexión a la base de datos'
    
    return render(request, 'analytics/dashboard.html', context)

def get_heatmap_data():
    """Generar mapa de calor con datos reales."""
    if db is None:
        return get_simulated_heatmap()
    
    try:
        start_date = datetime.now() - timedelta(days=30)
        consultations = list(db.consultations.find({
            'fecha_hora': {'$gte': start_date.isoformat()}
        }))
        
        days = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        hours = list(range(8, 21))
        matrix = np.zeros((len(hours), len(days)))
        
        day_map = {'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3, 
                   'Friday': 4, 'Saturday': 5, 'Sunday': 6}
        
        for consulta in consultations:
            fecha_hora = consulta.get('fecha_hora')
            if fecha_hora:
                try:
                    if isinstance(fecha_hora, str):
                        dt = datetime.fromisoformat(fecha_hora.replace('Z', '+00:00'))
                    else:
                        dt = fecha_hora
                    
                    hour = dt.hour
                    day_name = dt.strftime('%A')
                    
                    if 8 <= hour <= 20 and day_name in day_map:
                        day_idx = day_map[day_name]
                        hour_idx = hour - 8
                        matrix[hour_idx][day_idx] += 1
                except:
                    pass
        
        if matrix.sum() == 0:
            return get_simulated_heatmap()
        
        return {
            'z': matrix.tolist(),
            'x': days,
            'y': [f'{h}:00' for h in hours]
        }
    except Exception as e:
        print(f"Error en heatmap: {e}")
        return get_simulated_heatmap()

def get_simulated_heatmap():
    """Generar mapa de calor simulado cuando no hay datos."""
    np.random.seed(42)
    dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    horas = list(range(8, 21))
    data = np.random.randint(5, 30, size=(len(horas), len(dias)))
    
    for i, hora in enumerate(horas):
        if 10 <= hora <= 12:
            data[i] *= 1.5
        elif 16 <= hora <= 18:
            data[i] *= 1.3
    
    return {
        'z': data.tolist(),
        'x': dias,
        'y': [f'{h}:00' for h in horas]
    }

def get_demand_data():
    """Obtener datos de demanda histórica."""
    if db is None:
        return get_simulated_demand()
    
    try:
        start_date = datetime.now() - timedelta(days=30)
        consultations = list(db.consultations.find({
            'fecha_hora': {'$gte': start_date.isoformat()}
        }))
        
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
        
        if daily_counts:
            dates = sorted(daily_counts.keys())
            values = [daily_counts[d] for d in dates]
            return {'dates': dates, 'values': values}
        else:
            return get_simulated_demand()
    except:
        return get_simulated_demand()

def get_simulated_demand():
    dates = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(30, 0, -1)]
    values = [50 + (i * 0.5) + np.random.normal(0, 5) for i in range(30)]
    return {'dates': dates, 'values': values}

def get_forecast_data():
    """Generar pronóstico de demanda."""
    dates = [(datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(1, 8)]
    values = [55, 60, 58, 72, 80, 65, 55]
    return {'dates': dates, 'values': values}
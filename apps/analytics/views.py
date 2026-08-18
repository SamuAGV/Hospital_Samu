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

db = getattr(settings, 'mongo_db', None)

@login_required
def dashboard(request):
    """Dashboard de análisis."""
    context = {'page_title': 'Análisis Hospitalario'}
    
    if db is not None:
        try:
            # Obtener datos para gráficas
            context['heatmap_data'] = get_heatmap_data()
            context['demand_data'] = get_demand_data()
            context['forecast_data'] = get_forecast_data()
        except Exception as e:
            context['error'] = str(e)
    
    return render(request, 'analytics/dashboard.html', context)

@login_required
def heatmap_view(request):
    """Vista de mapa de calor."""
    context = {'page_title': 'Mapa de Calor - Demanda'}
    
    if db is not None:
        try:
            heatmap_data = get_heatmap_data()
            context['heatmap_json'] = json.dumps(heatmap_data, cls=plotly.utils.PlotlyJSONEncoder)
        except Exception as e:
            context['error'] = str(e)
    
    return render(request, 'analytics/heatmap.html', context)

@login_required
def demand_forecast(request):
    """Pronóstico de demanda."""
    if request.method == 'POST':
        try:
            # Aquí se implementaría la lógica de pronóstico
            forecast = generate_forecast()
            return JsonResponse({'forecast': forecast})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return render(request, 'analytics/demand.html')

def get_heatmap_data():
    """Generar datos para mapa de calor."""
    # Simular datos de demanda por hora y día
    dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    horas = list(range(8, 21))  # 8:00 a 20:00
    
    # Datos simulados (en producción vendrían de la BD)
    np.random.seed(42)
    data = np.random.randint(5, 30, size=(len(horas), len(dias)))
    
    # Aumentar demanda en horas pico
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
    # Simular datos de demanda diaria
    dates = [datetime.now() - timedelta(days=i) for i in range(30, 0, -1)]
    values = [50 + (i * 0.5) + np.random.normal(0, 5) for i in range(30)]
    
    return {
        'dates': [d.strftime('%Y-%m-%d') for d in dates],
        'values': values
    }

def get_forecast_data():
    """Generar pronóstico de demanda."""
    # Datos simulados para pronóstico
    dates = [datetime.now() + timedelta(days=i) for i in range(1, 8)]
    values = [55, 60, 58, 72, 80, 65, 55]
    
    return {
        'dates': [d.strftime('%Y-%m-%d') for d in dates],
        'values': values
    }

def generate_forecast():
    """Generar pronóstico simple."""
    # Pronóstico basado en promedio móvil
    return {
        'mañana': 'Alta demanda esperada en Cardiología',
        'horas_pico': '10:00 - 12:00',
        'especialidades': {
            'Cardiología': 'Alta',
            'Medicina General': 'Media',
            'Pediatría': 'Media',
            'Traumatología': 'Baja'
        }
    }
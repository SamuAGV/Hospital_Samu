from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings
from datetime import datetime, timedelta
import pandas as pd
import plotly.graph_objs as go
import plotly.utils
import json
from django.http import JsonResponse
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


# Import MongoDB connection
try:
    db = settings.mongo_db
except:
    db = None

@login_required(login_url='/users/login/')
def dashboard(request):
    """Vista principal del dashboard."""
    
    context = {
        'page_title': 'Dashboard General',
        'user': request.user,
        'current_date': datetime.now().strftime('%d/%m/%Y %H:%M'),
    }
    
    # Si MongoDB está conectado, obtener datos reales
    if db is not None:
        try:
            # CONTAR PACIENTES REALES
            patients_count = db.patients.count_documents({})
            context['patients_count'] = patients_count
            
            # CONTAR CONSULTAS REALES
            consultations_count = db.consultations.count_documents({})
            context['consultations_count'] = consultations_count
            
            # CONTAR CITAS REALES (solo programadas)
            appointments_count = db.appointments.count_documents({'estado': 'Programada'})
            context['appointments_count'] = appointments_count
            
            # CONTAR HOSPITALIZACIONES ACTIVAS REALES
            active_hospitalizations = db.hospitalizations.count_documents({'estado': 'Activa'})
            context['active_hospitalizations'] = active_hospitalizations
            
            # OBTENER DEMANDA REAL DE CONSULTAS POR DÍA
            demand_data = get_demand_data()
            context['demand_chart'] = json.dumps(demand_data, cls=plotly.utils.PlotlyJSONEncoder)
            
        except Exception as e:
            context['error'] = str(e)
            # Si hay error, poner valores en 0
            context['patients_count'] = 0
            context['consultations_count'] = 0
            context['appointments_count'] = 0
            context['active_hospitalizations'] = 0
            context['demand_chart'] = json.dumps(get_empty_demand_chart(), cls=plotly.utils.PlotlyJSONEncoder)
    else:
        # Si NO hay conexión a MongoDB, poner todo en 0
        context['patients_count'] = 0
        context['consultations_count'] = 0
        context['appointments_count'] = 0
        context['active_hospitalizations'] = 0
        context['demand_chart'] = json.dumps(get_empty_demand_chart(), cls=plotly.utils.PlotlyJSONEncoder)
        context['error'] = 'No hay conexión a la base de datos'
    
    return render(request, 'core/dashboard.html', context)

def get_demand_data():
    """Obtener datos de demanda real de la base de datos."""
    if db is None:
        return get_empty_demand_chart()
    
    try:
        # Obtener consultas de los últimos 30 días
        from datetime import timedelta
        today = datetime.now()
        start_date = today - timedelta(days=30)
        
        # Pipeline de agregación para contar consultas por día
        pipeline = [
            {
                '$match': {
                    'fecha_hora': {'$gte': start_date.isoformat()}
                }
            },
            {
                '$group': {
                    '_id': {'$dateToString': {'format': '%Y-%m-%d', 'date': '$fecha_hora'}},
                    'total': {'$sum': 1}
                }
            },
            {'$sort': {'_id': 1}}
        ]
        
        result = list(db.consultations.aggregate(pipeline))
        
        if result:
            dates = [item['_id'] for item in result]
            values = [item['total'] for item in result]
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=dates,
                y=values,
                mode='lines+markers',
                name='Consultas diarias',
                line=dict(color='#0d47a1', width=3),
                marker=dict(size=8, color='#1565c0')
            ))
            
            fig.update_layout(
                title='Evolución de Consultas Diarias',
                xaxis_title='Fecha',
                yaxis_title='Número de Consultas',
                height=350,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Arial, sans-serif"),
                hovermode='x unified'
            )
            
            return fig
        else:
            return get_empty_demand_chart()
            
    except Exception as e:
        print(f"Error en get_demand_data: {e}")
        return get_empty_demand_chart()

def get_empty_demand_chart():
    """Retornar gráfica vacía cuando no hay datos."""
    fig = go.Figure()
    fig.add_annotation(
        text="No hay datos de consultas disponibles",
        xref="paper", yref="paper",
        x=0.5, y=0.5,
        showarrow=False,
        font=dict(size=14, color="#9e9e9e")
    )
    fig.update_layout(
        height=350,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False, zeroline=False, visible=False),
        yaxis=dict(showgrid=False, zeroline=False, visible=False)
    )
    return fig

def test_mongodb(request):
    """Endpoint para probar la conexión a MongoDB."""
    data = {
        'connected': settings.MONGO_CONNECTED,
        'db_name': settings.MONGO_DB_NAME,
        'mongo_db': str(settings.MONGO_DB),
    }
    
    if settings.MONGO_CONNECTED and settings.MONGO_DB is not None:
        try:
            db = settings.MONGO_DB
            users_collection = db['users']
            count = users_collection.count_documents({})
            data['users_count'] = count
            data['status'] = 'OK'
        except Exception as e:
            data['error'] = str(e)
            data['status'] = 'ERROR'
    else:
        data['status'] = 'DISCONNECTED'
    
    return JsonResponse(data)
def test_mongodb(request):
    """Endpoint para probar la conexión a MongoDB."""
    data = {
        'connected': settings.MONGO_CONNECTED,
        'db_name': settings.MONGO_DB_NAME,
        'mongo_uri_prefix': settings.MONGO_URI[:30] if settings.MONGO_URI else None,
    }
    
    if settings.MONGO_CONNECTED and settings.MONGO_DB is not None:
        try:
            db = settings.MONGO_DB
            users_collection = db['users']
            count = users_collection.count_documents({})
            data['users_count'] = count
            data['status'] = 'OK'
            
            # Listar usuarios (solo para depuración)
            users = list(users_collection.find({}, {'username': 1, 'email': 1, '_id': 0}))
            data['users'] = users
            
            logger.info(f"Test MongoDB exitoso: {count} usuarios")
        except Exception as e:
            data['error'] = str(e)
            data['status'] = 'ERROR'
            logger.error(f"Error en test MongoDB: {e}")
    else:
        data['status'] = 'DISCONNECTED'
        logger.error(" MongoDB no conectado en test")
    
    return JsonResponse(data)

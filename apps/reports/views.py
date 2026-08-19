from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from datetime import datetime, timedelta  # <--- ¡AGREGADO timedelta AQUÍ!
import pandas as pd
import json

# Usar la variable correcta de MongoDB
db = getattr(settings, 'MONGO_DB', None)

@login_required
def dashboard(request):
    """Dashboard de reportes."""
    context = {'page_title': 'Reportes'}
    return render(request, 'reports/dashboard.html', context)

@login_required
def appointments_report(request):
    """Reporte de citas."""
    context = {'page_title': 'Reporte de Citas'}
    
    if db is not None:
        try:
            # Obtener filtros
            fecha_inicio = request.GET.get('fecha_inicio')
            fecha_fin = request.GET.get('fecha_fin')
            
            query = {}
            if fecha_inicio and fecha_fin:
                query['fecha_hora'] = {'$gte': fecha_inicio, '$lte': fecha_fin}
            
            appointments = list(db.appointments.find(query, {'_id': 0}))
            
            if appointments:
                df = pd.DataFrame(appointments)
                context['total'] = len(df)
                context['por_estado'] = df['estado'].value_counts().to_dict()
                context['appointments'] = appointments
            else:
                context['total'] = 0
                context['por_estado'] = {}
                context['appointments'] = []
                
        except Exception as e:
            messages.error(request, f'Error al generar reporte: {e}')
            context['total'] = 0
            context['por_estado'] = {}
            context['appointments'] = []
    
    # Si no hay conexión, valores por defecto
    else:
        context['total'] = 0
        context['por_estado'] = {}
        context['appointments'] = []
    
    return render(request, 'reports/appointments.html', context)

@login_required
def consultations_report(request):
    """Reporte de consultas."""
    context = {'page_title': 'Reporte de Consultas'}
    
    if db is not None:
        try:
            consultations = list(db.consultations.find({}, {'_id': 0}))
            context['consultations'] = consultations
            context['total'] = len(consultations)
            
        except Exception as e:
            messages.error(request, f'Error al generar reporte: {e}')
            context['consultations'] = []
            context['total'] = 0
    else:
        context['consultations'] = []
        context['total'] = 0
    
    return render(request, 'reports/consultations.html', context)

@login_required
def occupancy_report(request):
    """Reporte de ocupación con filtros y buscador."""
    context = {'page_title': 'Reporte de Ocupación'}
    
    # Obtener filtros de la URL
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    area = request.GET.get('area', '').strip()
    
    # Guardar los filtros en el contexto para mantenerlos en el formulario
    context['fecha_inicio'] = fecha_inicio
    context['fecha_fin'] = fecha_fin
    context['area'] = area
    
    if db is not None and settings.MONGO_CONNECTED:
        try:
            total_camas = 120
            ocupadas = db.hospitalizations.count_documents({'estado': 'Activa'})
            
            context['total_camas'] = total_camas
            context['camas_ocupadas'] = ocupadas
            context['porcentaje'] = round((ocupadas / total_camas) * 100, 1) if total_camas > 0 else 0
            context['camas_disponibles'] = total_camas - ocupadas
            
            # --- GENERACIÓN DEL HISTORIAL CON FILTROS ---
            query_historico = {}
            
            # Filtro por fecha (si se proporciona)
            if fecha_inicio and fecha_fin:
                query_historico['fecha_ingreso'] = {'$gte': fecha_inicio, '$lte': fecha_fin}
            
            # Filtro por área (si se proporciona)
            if area:
                query_historico['especialidad'] = area
            
            # Obtener hospitalizaciones filtradas para el histórico
            hospitalizaciones_filtradas = list(db.hospitalizations.find(query_historico, {'_id': 0}))
            
            # Generar histórico (simulación basada en los datos obtenidos)
            historico = []
            if hospitalizaciones_filtradas:
                # Agrupar por fecha (simulación simple)
                from collections import defaultdict
                counts = defaultdict(int)
                for h in hospitalizaciones_filtradas:
                    fecha = h.get('fecha_ingreso', '')[:10]  # Tomar solo la fecha (YYYY-MM-DD)
                    counts[fecha] += 1
                
                for fecha, count in sorted(counts.items()):
                    historico.append({
                        'fecha': fecha,
                        'ocupacion': round((count / total_camas) * 100, 1)
                    })
            else:
                # Si no hay datos, mostrar un mensaje
                historico = []
            
            context['historico'] = historico
            
        except Exception as e:
            messages.error(request, f'Error al generar reporte: {e}')
            # Fallback en caso de error
            context['total_camas'] = 120
            context['camas_ocupadas'] = 0
            context['porcentaje'] = 0
            context['camas_disponibles'] = 120
            context['historico'] = []
    else:
        context['total_camas'] = 120
        context['camas_ocupadas'] = 0
        context['porcentaje'] = 0
        context['camas_disponibles'] = 120
        context['historico'] = []
    
    return render(request, 'reports/occupancy.html', context)

@login_required
def ml_report(request):
    """Reporte de Machine Learning."""
    context = {'page_title': 'Reporte ML'}
    return render(request, 'reports/ml.html', context)

@login_required
def export_report(request, report_type):
    """Exportar reporte."""
    try:
        # Aquí se implementaría la exportación a CSV, Excel o PDF
        return JsonResponse({
            'status': 'success',
            'message': f'Reporte {report_type} exportado correctamente'
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
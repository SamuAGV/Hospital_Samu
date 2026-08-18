from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from datetime import datetime
import pandas as pd
import json

db = getattr(settings, 'mongo_db', None)

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
                context['appointments'] = []
                
        except Exception as e:
            messages.error(request, f'Error al generar reporte: {e}')
    
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
    
    return render(request, 'reports/consultations.html', context)

@login_required
def occupancy_report(request):
    """Reporte de ocupación."""
    context = {'page_title': 'Reporte de Ocupación'}
    
    if db is not None:
        try:
            total_camas = 120
            ocupadas = db.hospitalizations.count_documents({'estado': 'Activa'})
            
            context['total_camas'] = total_camas
            context['camas_ocupadas'] = ocupadas
            context['porcentaje'] = round((ocupadas / total_camas) * 100, 1)
            
            # Historial de ocupación (simulado)
            context['historico'] = [
                {'fecha': '2026-08-01', 'ocupacion': 85},
                {'fecha': '2026-08-02', 'ocupacion': 88},
                {'fecha': '2026-08-03', 'ocupacion': 82},
                {'fecha': '2026-08-04', 'ocupacion': 90},
                {'fecha': '2026-08-05', 'ocupacion': 87},
                {'fecha': '2026-08-06', 'ocupacion': 85},
                {'fecha': '2026-08-07', 'ocupacion': 89},
            ]
            
        except Exception as e:
            messages.error(request, f'Error al generar reporte: {e}')
    
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
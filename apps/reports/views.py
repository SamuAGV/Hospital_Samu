from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import datetime, timedelta
from io import BytesIO
import pandas as pd
import csv
import json

# Intentar importar xhtml2pdf para PDF
try:
    from xhtml2pdf import pisa
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

db = getattr(settings, 'MONGO_DB', None)

# ================= UTILIDAD PARA PDF =================
def render_to_pdf(template_src, context_dict={}):
    """Renderiza un template a PDF usando xhtml2pdf."""
    if not PDF_AVAILABLE:
        return None
    
    from django.template.loader import get_template
    from django.http import HttpResponse
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

# ================= DASHBOARD =================
@login_required
def dashboard(request):
    context = {'page_title': 'Reportes'}
    return render(request, 'reports/dashboard.html', context)

# ================= REPORTE DE CITAS (CON FILTROS Y PAGINACIÓN) =================
@login_required
def appointments_report(request):
    context = {'page_title': 'Reporte de Citas'}
    
    # Obtener filtros de la URL
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    estado = request.GET.get('estado', '').strip()
    
    context['fecha_inicio'] = fecha_inicio
    context['fecha_fin'] = fecha_fin
    context['estado'] = estado
    
    if db is not None:
        try:
            # Construir query dinámica
            query = {}
            if fecha_inicio and fecha_fin:
                query['fecha_hora'] = {'$gte': fecha_inicio, '$lte': fecha_fin}
            if estado:
                query['estado'] = estado
            
            # Obtener todas las citas filtradas para estadísticas
            all_appointments = list(db.appointments.find(query, {'_id': 0}))
            
            if all_appointments:
                df = pd.DataFrame(all_appointments)
                context['total'] = len(df)
                context['por_estado'] = df['estado'].value_counts().to_dict()
                
                # Paginación
                paginator = Paginator(all_appointments, 20)  # 20 items por página
                page = request.GET.get('page', 1)
                try:
                    appointments = paginator.page(page)
                except PageNotAnInteger:
                    appointments = paginator.page(1)
                except EmptyPage:
                    appointments = paginator.page(paginator.num_pages)
                
                context['appointments'] = appointments
                context['is_paginated'] = True
                context['paginator'] = paginator
                context['page_obj'] = appointments
            else:
                context['total'] = 0
                context['por_estado'] = {}
                context['appointments'] = []
                context['is_paginated'] = False
                
        except Exception as e:
            messages.error(request, f'Error al generar reporte: {e}')
            context['total'] = 0
            context['por_estado'] = {}
            context['appointments'] = []
            context['is_paginated'] = False
    else:
        context['total'] = 0
        context['por_estado'] = {}
        context['appointments'] = []
        context['is_paginated'] = False
    
    return render(request, 'reports/appointments.html', context)

# ================= REPORTE DE CONSULTAS (CON FILTROS Y PAGINACIÓN) =================
@login_required
def consultations_report(request):
    context = {'page_title': 'Reporte de Consultas'}
    
    # Obtener filtros de la URL
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    tipo_consulta = request.GET.get('tipo_consulta', '').strip()
    
    context['fecha_inicio'] = fecha_inicio
    context['fecha_fin'] = fecha_fin
    context['tipo_consulta'] = tipo_consulta
    
    if db is not None:
        try:
            # Construir query dinámica
            query = {}
            if fecha_inicio and fecha_fin:
                query['fecha_hora'] = {'$gte': fecha_inicio, '$lte': fecha_fin}
            if tipo_consulta:
                query['tipo_consulta'] = tipo_consulta
            
            # Obtener todas las consultas filtradas
            all_consultations = list(db.consultations.find(query, {'_id': 0}))
            
            if all_consultations:
                context['total'] = len(all_consultations)
                
                # Paginación
                paginator = Paginator(all_consultations, 20)
                page = request.GET.get('page', 1)
                try:
                    consultations = paginator.page(page)
                except PageNotAnInteger:
                    consultations = paginator.page(1)
                except EmptyPage:
                    consultations = paginator.page(paginator.num_pages)
                
                context['consultations'] = consultations
                context['is_paginated'] = True
                context['paginator'] = paginator
                context['page_obj'] = consultations
            else:
                context['total'] = 0
                context['consultations'] = []
                context['is_paginated'] = False
                
        except Exception as e:
            messages.error(request, f'Error al generar reporte: {e}')
            context['total'] = 0
            context['consultations'] = []
            context['is_paginated'] = False
    else:
        context['total'] = 0
        context['consultations'] = []
        context['is_paginated'] = False
    
    return render(request, 'reports/consultations.html', context)

# ================= REPORTE DE OCUPACIÓN (CON FILTROS) =================
@login_required
def occupancy_report(request):
    context = {'page_title': 'Reporte de Ocupación'}
    
    # Obtener filtros de la URL
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    area = request.GET.get('area', '').strip()
    
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
            
            # Generación del historial con filtros
            query_historico = {}
            if fecha_inicio and fecha_fin:
                query_historico['fecha_ingreso'] = {'$gte': fecha_inicio, '$lte': fecha_fin}
            if area:
                query_historico['especialidad'] = area
            
            hospitalizaciones_filtradas = list(db.hospitalizations.find(query_historico, {'_id': 0}))
            
            from collections import defaultdict
            counts = defaultdict(int)
            for h in hospitalizaciones_filtradas:
                fecha = h.get('fecha_ingreso', '')[:10]
                counts[fecha] += 1
            
            historico = []
            for fecha, count in sorted(counts.items()):
                historico.append({
                    'fecha': fecha,
                    'ocupacion': round((count / total_camas) * 100, 1)
                })
            
            context['historico'] = historico
            
        except Exception as e:
            messages.error(request, f'Error al generar reporte: {e}')
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

# ================= EXPORTAR REPORTE (CSV, EXCEL, PDF) CON FILTROS =================
@login_required
def export_report(request, report_type):
    """Exportar reporte a CSV, Excel o PDF respetando los filtros."""
    try:
        formato = request.GET.get('formato', 'csv').lower()
        
        # CAPTURAR LOS FILTROS DE LA URL
        fecha_inicio = request.GET.get('fecha_inicio')
        fecha_fin = request.GET.get('fecha_fin')
        estado = request.GET.get('estado', '').strip()
        tipo_consulta = request.GET.get('tipo_consulta', '').strip()
        area = request.GET.get('area', '').strip()
        
        if db is None:
            return JsonResponse({'status': 'error', 'message': 'Base de datos no disponible'}, status=500)
        
        # Construir la query según el tipo de reporte
        query = {}
        data = []
        filename = ''
        
        if report_type == 'appointments':
            if fecha_inicio and fecha_fin:
                query['fecha_hora'] = {'$gte': fecha_inicio, '$lte': fecha_fin}
            if estado:
                query['estado'] = estado
            data = list(db.appointments.find(query, {'_id': 0}))
            filename = 'reporte_citas'
            
        elif report_type == 'consultations':
            if fecha_inicio and fecha_fin:
                query['fecha_hora'] = {'$gte': fecha_inicio, '$lte': fecha_fin}
            if tipo_consulta:
                query['tipo_consulta'] = tipo_consulta
            data = list(db.consultations.find(query, {'_id': 0}))
            filename = 'reporte_consultas'
            
        elif report_type == 'occupancy':
            if fecha_inicio and fecha_fin:
                query['fecha_ingreso'] = {'$gte': fecha_inicio, '$lte': fecha_fin}
            if area:
                query['especialidad'] = area
            data = list(db.hospitalizations.find(query, {'_id': 0}))
            filename = 'reporte_ocupacion'
            
        else:
            return JsonResponse({'status': 'error', 'message': 'Tipo de reporte no válido'}, status=400)
        
        if not data:
            return JsonResponse({'status': 'error', 'message': 'No hay datos para exportar con esos filtros'}, status=404)
        
        # Convertir a DataFrame
        df = pd.DataFrame(data)
        
        # EXPORTAR CSV
        if formato == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{filename}.csv"'
            df.to_csv(response, index=False)
            return response
        
        # EXPORTAR EXCEL
        elif formato == 'excel':
            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename="{filename}.xlsx"'
            df.to_excel(response, index=False)
            return response
        
        # EXPORTAR PDF (corregido para pasar los headers)
        elif formato == 'pdf':
            # Obtener los nombres de las columnas
            headers = list(df.columns)
            
            context = {
                'data': data,
                'headers': headers,
                'report_type': report_type,
                'fecha_exportacion': datetime.now().strftime('%d/%m/%Y %H:%M'),
                'total_registros': len(data)
            }
            pdf = render_to_pdf('reports/pdf_template.html', context)
            if pdf:
                response = HttpResponse(pdf, content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="{filename}.pdf"'
                return response
            else:
                return JsonResponse({'status': 'error', 'message': 'Error generando PDF (verifica xhtml2pdf)'}, status=500)
        
        else:
            return JsonResponse({'status': 'error', 'message': 'Formato no soportado'}, status=400)
            
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

# ================= REPORTE ML =================
@login_required
def ml_report(request):
    context = {'page_title': 'Reporte ML'}
    return render(request, 'reports/ml.html', context)
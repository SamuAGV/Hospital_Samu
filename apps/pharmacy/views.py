from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import datetime, timedelta
import pandas as pd

db = settings.MONGO_DB if hasattr(settings, 'MONGO_DB') else None

@login_required
def dashboard(request):
    """Dashboard de farmacia."""
    context = {'page_title': 'Farmacia e Inventario'}
    
    if db is not None and settings.MONGO_CONNECTED:
        try:
            medicines_cursor = db.medicines.find({})
            medicines_list = list(medicines_cursor)
            
            for m in medicines_list:
                m['id'] = str(m['_id'])
            
            context['medicines'] = medicines_list
            context['total'] = len(medicines_list)
            
            # Medicamentos con bajo stock
            low_stock = [m for m in medicines_list if m.get('stock', 0) <= m.get('stock_minimo', 10)]
            context['low_stock'] = len(low_stock)
            
            # Medicamentos próximos a caducar (30 días)
            today = datetime.now()
            expiring = []
            for m in medicines_list:
                if 'fecha_caducidad' in m:
                    fecha_cad = datetime.fromisoformat(m['fecha_caducidad'])
                    if (fecha_cad - today).days <= 30:
                        expiring.append(m)
            context['expiring'] = len(expiring)
            
            # Valor total del inventario
            total_value = sum(m.get('stock', 0) * m.get('precio_unitario', 0) for m in medicines_list)
            context['total_value'] = total_value
            
        except Exception as e:
            messages.error(request, f'Error al cargar farmacia: {e}')
            context['medicines'] = []
            context['total'] = 0
            context['low_stock'] = 0
            context['expiring'] = 0
            context['total_value'] = 0
    else:
        context['medicines'] = []
        context['total'] = 0
        context['low_stock'] = 0
        context['expiring'] = 0
        context['total_value'] = 0
    
    return render(request, 'pharmacy/dashboard.html', context)

@login_required
def list_medicines(request):
    """Listar medicamentos con paginación."""
    context = {'page_title': 'Medicamentos'}
    
    if db is not None and settings.MONGO_CONNECTED:
        try:
            medicines_cursor = db.medicines.find({})
            medicines_list = list(medicines_cursor)
            
            for m in medicines_list:
                m['id'] = str(m['_id'])
            
            # Paginación
            paginator = Paginator(medicines_list, 20)
            page = request.GET.get('page', 1)
            
            try:
                medicines = paginator.page(page)
            except PageNotAnInteger:
                medicines = paginator.page(1)
            except EmptyPage:
                medicines = paginator.page(paginator.num_pages)
            
            context['medicines'] = medicines
            context['total'] = len(medicines_list)
            context['is_paginated'] = True
            context['paginator'] = paginator
            context['page_obj'] = medicines
            
        except Exception as e:
            messages.error(request, f'Error al cargar medicamentos: {e}')
            context['medicines'] = []
            context['total'] = 0
            context['is_paginated'] = False
    else:
        context['medicines'] = []
        context['total'] = 0
        context['is_paginated'] = False
    
    return render(request, 'pharmacy/list_medicines.html', context)

# ... resto de funciones (create_medicine, medicine_detail, etc.)
@login_required
def create_medicine(request):
    """Crear un nuevo medicamento."""
    if request.method == 'POST':
        try:
            medicine_data = {
                'nombre': request.POST.get('nombre'),
                'principio_activo': request.POST.get('principio_activo'),
                'presentacion': request.POST.get('presentacion'),
                'concentracion': request.POST.get('concentracion'),
                'precio_unitario': float(request.POST.get('precio_unitario', 0)),
                'stock': int(request.POST.get('stock', 0)),
                'stock_minimo': int(request.POST.get('stock_minimo', 10)),
                'requiere_receta': request.POST.get('requiere_receta') == 'on',
                'fecha_registro': datetime.now().isoformat(),
                'activo': True
            }
            
            if db is not None:
                db.medicines.insert_one(medicine_data)
                messages.success(request, 'Medicamento registrado correctamente')
                return redirect('pharmacy:list_medicines')
                
        except Exception as e:
            messages.error(request, f'Error al registrar medicamento: {e}')
    
    return render(request, 'pharmacy/create_medicine.html')

@login_required
def medicine_detail(request, medicine_id):
    """Ver detalle de medicamento."""
    context = {'page_title': 'Detalle de Medicamento'}
    
    if db is not None:
        try:
            from bson import ObjectId
            medicine = db.medicines.find_one({'_id': ObjectId(medicine_id)})
            if medicine:
                medicine['id'] = str(medicine['_id'])
                context['medicine'] = medicine
            else:
                messages.error(request, 'Medicamento no encontrado')
                return redirect('pharmacy:list_medicines')
        except Exception as e:
            messages.error(request, f'Error al cargar: {e}')
            return redirect('pharmacy:list_medicines')
    
    return render(request, 'pharmacy/medicine_detail.html', context)

@login_required
def inventory_view(request):
    """Ver inventario."""
    context = {'page_title': 'Inventario'}
    
    if db is not None:
        try:
            # Movimientos de inventario
            inventory = list(db.inventory.find({}, {'_id': 0}).sort('fecha', -1).limit(100))
            context['inventory'] = inventory
            context['total'] = len(inventory)
            
        except Exception as e:
            messages.error(request, f'Error al cargar inventario: {e}')
            context['inventory'] = []
    
    return render(request, 'pharmacy/inventory.html', context)

@login_required
def add_inventory(request):
    """Agregar movimiento de inventario."""
    if request.method == 'POST':
        try:
            inventory_data = {
                'id_medicamento': request.POST.get('id_medicamento'),
                'tipo_movimiento': request.POST.get('tipo_movimiento'),
                'cantidad': int(request.POST.get('cantidad', 0)),
                'fecha': datetime.now().isoformat(),
                'responsable': request.user.username,
                'observaciones': request.POST.get('observaciones')
            }
            
            if db is not None:
                db.inventory.insert_one(inventory_data)
                
                # Actualizar stock del medicamento
                from bson import ObjectId
                medicamento_id = ObjectId(request.POST.get('id_medicamento'))
                cantidad = int(request.POST.get('cantidad', 0))
                tipo = request.POST.get('tipo_movimiento')
                
                if tipo == 'Entrada':
                    db.medicines.update_one(
                        {'_id': medicamento_id},
                        {'$inc': {'stock': cantidad}}
                    )
                else:
                    db.medicines.update_one(
                        {'_id': medicamento_id},
                        {'$inc': {'stock': -cantidad}}
                    )
                
                messages.success(request, 'Movimiento registrado correctamente')
                return redirect('pharmacy:inventory')
                
        except Exception as e:
            messages.error(request, f'Error al registrar movimiento: {e}')
    
    context = {'page_title': 'Nuevo Movimiento de Inventario'}
    if db is not None:
        context['medicines'] = list(db.medicines.find({}, {'_id': 0}))
    
    return render(request, 'pharmacy/add_inventory.html', context)

@login_required
def alerts_view(request):
    """Ver alertas de farmacia."""
    context = {'page_title': 'Alertas de Farmacia'}
    alerts = []
    
    if db is not None:
        try:
            medicines = list(db.medicines.find({}, {'_id': 0}))
            
            # Alertas de bajo stock
            for m in medicines:
                if m.get('stock', 0) <= m.get('stock_minimo', 10):
                    alerts.append({
                        'tipo': 'Bajo Stock',
                        'medicamento': m['nombre'],
                        'mensaje': f'Stock actual: {m.get("stock", 0)} (Mínimo: {m.get("stock_minimo", 10)})',
                        'prioridad': 'Alta' if m.get('stock', 0) == 0 else 'Media'
                    })
            
            # Alertas de caducidad
            today = datetime.now()
            for m in medicines:
                if 'fecha_caducidad' in m:
                    fecha_cad = datetime.fromisoformat(m['fecha_caducidad'])
                    dias = (fecha_cad - today).days
                    if 0 <= dias <= 30:
                        alerts.append({
                            'tipo': 'Próximo a Caducar',
                            'medicamento': m['nombre'],
                            'mensaje': f'Caduca en {dias} días',
                            'prioridad': 'Alta' if dias <= 7 else 'Media'
                        })
            
            context['alerts'] = alerts
            context['total'] = len(alerts)
            
        except Exception as e:
            messages.error(request, f'Error al cargar alertas: {e}')
    
    return render(request, 'pharmacy/alerts.html', context)
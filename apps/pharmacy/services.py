"""
Servicios para el módulo de Farmacia
"""
from django.conf import settings
from datetime import datetime, timedelta

db = getattr(settings, 'mongo_db', None)

class PharmacyService:
    """Servicios para farmacia."""
    
    @staticmethod
    def get_inventory_stats():
        """Obtener estadísticas de inventario."""
        if db is None:
            return None
        
        try:
            medicines = list(db.medicines.find({}, {'_id': 0}))
            
            # Total de medicamentos
            total = len(medicines)
            
            # Bajo stock
            low_stock = [m for m in medicines if m.get('stock', 0) <= m.get('stock_minimo', 10)]
            
            # Próximos a caducar
            today = datetime.now()
            expiring = []
            for m in medicines:
                if 'fecha_caducidad' in m:
                    fecha_cad = datetime.fromisoformat(m['fecha_caducidad'])
                    if (fecha_cad - today).days <= 30:
                        expiring.append(m)
            
            # Valor total del inventario
            total_value = sum(m.get('stock', 0) * m.get('precio_unitario', 0) for m in medicines)
            
            return {
                'total_medicines': total,
                'low_stock': len(low_stock),
                'expiring': len(expiring),
                'total_value': total_value
            }
        except Exception as e:
            print(f"Error en get_inventory_stats: {e}")
            return None
    
    @staticmethod
    def get_alerts():
        """Obtener alertas de farmacia."""
        if db is None:
            return []
        
        try:
            medicines = list(db.medicines.find({}, {'_id': 0}))
            alerts = []
            today = datetime.now()
            
            for m in medicines:
                # Alerta de bajo stock
                if m.get('stock', 0) <= m.get('stock_minimo', 10):
                    alerts.append({
                        'tipo': 'Bajo Stock',
                        'medicamento': m['nombre'],
                        'mensaje': f"Stock: {m.get('stock', 0)} (Mínimo: {m.get('stock_minimo', 10)})",
                        'prioridad': 'Alta' if m.get('stock', 0) == 0 else 'Media'
                    })
                
                # Alerta de caducidad
                if 'fecha_caducidad' in m:
                    fecha_cad = datetime.fromisoformat(m['fecha_caducidad'])
                    dias = (fecha_cad - today).days
                    if 0 <= dias <= 30:
                        alerts.append({
                            'tipo': 'Próximo a Caducar',
                            'medicamento': m['nombre'],
                            'mensaje': f"Caduca en {dias} días",
                            'prioridad': 'Alta' if dias <= 7 else 'Media'
                        })
            
            return alerts
        except Exception as e:
            print(f"Error en get_alerts: {e}")
            return []
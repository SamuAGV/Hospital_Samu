"""
Servicios para el módulo de Hospitalización
"""
from django.conf import settings
from datetime import datetime, timedelta

db = getattr(settings, 'mongo_db', None)

class HospitalizationService:
    """Servicios para hospitalización."""
    
    @staticmethod
    def get_occupancy_stats():
        """Obtener estadísticas de ocupación."""
        if db is None:
            return None
        
        try:
            total_camas = 120
            ocupadas = db.hospitalizations.count_documents({'estado': 'Activa'})
            
            # Ocupación por área (simulada con datos de la BD)
            areas = []
            especialidades = list(db.specialties.find({}, {'_id': 0}))
            for esp in especialidades[:6]:
                count = db.hospitalizations.count_documents({
                    'estado': 'Activa',
                    'especialidad': esp.get('nombre')
                })
                areas.append({
                    'area': esp.get('nombre', 'General'),
                    'ocupadas': count,
                    'total': 15
                })
            
            return {
                'total_camas': total_camas,
                'camas_ocupadas': ocupadas,
                'porcentaje': round((ocupadas / total_camas) * 100, 1),
                'areas': areas
            }
        except Exception as e:
            print(f"Error en get_occupancy_stats: {e}")
            return None
    
    @staticmethod
    def get_active_patients():
        """Obtener pacientes activos hospitalizados."""
        if db is None:
            return []
        
        try:
            patients = list(db.hospitalizations.find(
                {'estado': 'Activa'},
                {'_id': 0}
            ).sort('fecha_ingreso', -1))
            return patients
        except Exception as e:
            print(f"Error en get_active_patients: {e}")
            return []
    
    @staticmethod
    def get_discharge_stats():
        """Obtener estadísticas de altas."""
        if db is None:
            return None
        
        try:
            # Altas del mes actual
            today = datetime.now()
            month_start = datetime(today.year, today.month, 1)
            month_start_str = month_start.isoformat()
            
            discharges = db.hospitalizations.count_documents({
                'estado': 'Alta',
                'fecha_alta': {'$gte': month_start_str}
            })
            
            # Estancia promedio
            pipeline = [
                {'$match': {'estado': 'Alta'}},
                {'$group': {
                    '_id': None,
                    'avg_stay': {'$avg': {'$subtract': ['$fecha_alta', '$fecha_ingreso']}}
                }}
            ]
            result = list(db.hospitalizations.aggregate(pipeline))
            
            return {
                'monthly_discharges': discharges,
                'avg_stay_days': round(result[0]['avg_stay'] / (1000*60*60*24), 1) if result else 0
            }
        except Exception as e:
            print(f"Error en get_discharge_stats: {e}")
            return None
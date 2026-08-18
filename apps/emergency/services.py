"""
Servicios para el módulo de Urgencias
"""
from django.conf import settings
from datetime import datetime, timedelta

db = getattr(settings, 'mongo_db', None)

class EmergencyService:
    """Servicios para urgencias."""
    
    @staticmethod
    def get_daily_stats():
        """Obtener estadísticas diarias de urgencias."""
        if db is None:
            return None
        
        try:
            today = datetime.now().date()
            today_start = datetime.combine(today, datetime.min.time())
            
            # Pacientes del día
            today_patients = db.emergencies.count_documents({
                'fecha_hora_ingreso': {'$gte': today_start.isoformat()}
            })
            
            # Por prioridad
            priorities = db.emergencies.aggregate([
                {'$match': {'fecha_hora_ingreso': {'$gte': today_start.isoformat()}}},
                {'$group': {'_id': '$prioridad', 'count': {'$sum': 1}}}
            ])
            
            priority_counts = {p['_id']: p['count'] for p in priorities}
            
            # Tiempo promedio de espera (simulado)
            avg_wait = 15  # minutos
            
            return {
                'today_patients': today_patients,
                'priorities': priority_counts,
                'avg_wait_time': avg_wait
            }
        except Exception as e:
            print(f"Error en get_daily_stats: {e}")
            return None
    
    @staticmethod
    def get_peak_hours():
        """Obtener horas de mayor demanda."""
        if db is None:
            return []
        
        try:
            pipeline = [
                {'$group': {
                    '_id': {'$hour': '$fecha_hora_ingreso'},
                    'count': {'$sum': 1}
                }},
                {'$sort': {'count': -1}},
                {'$limit': 5}
            ]
            hours = list(db.emergencies.aggregate(pipeline))
            return hours
        except Exception as e:
            print(f"Error en get_peak_hours: {e}")
            return []
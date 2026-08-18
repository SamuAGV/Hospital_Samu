"""
Servicios para el módulo de Laboratorio
"""
from django.conf import settings
from datetime import datetime, timedelta

db = getattr(settings, 'mongo_db', None)

class LaboratoryService:
    """Servicios para laboratorio."""
    
    @staticmethod
    def get_stats():
        """Obtener estadísticas de laboratorio."""
        if db is None:
            return None
        
        try:
            # Total de solicitudes
            total = db.lab_requests.count_documents({})
            
            # Por estado
            status_counts = db.lab_requests.aggregate([
                {'$group': {'_id': '$estado', 'count': {'$sum': 1}}}
            ])
            status = {s['_id']: s['count'] for s in status_counts}
            
            # Por tipo de estudio
            type_counts = db.lab_requests.aggregate([
                {'$group': {'_id': '$tipo_estudio', 'count': {'$sum': 1}}},
                {'$sort': {'count': -1}},
                {'$limit': 5}
            ])
            types = [{'nombre': t['_id'], 'cantidad': t['count']} for t in type_counts]
            
            return {
                'total': total,
                'status': status,
                'top_types': types
            }
        except Exception as e:
            print(f"Error en get_stats: {e}")
            return None
    
    @staticmethod
    def get_pending_requests():
        """Obtener solicitudes pendientes."""
        if db is None:
            return []
        
        try:
            requests = list(db.lab_requests.find(
                {'estado': {'$in': ['Solicitado', 'En Proceso']}},
                {'_id': 0}
            ).sort('fecha_solicitud', 1))
            return requests
        except Exception as e:
            print(f"Error en get_pending_requests: {e}")
            return []
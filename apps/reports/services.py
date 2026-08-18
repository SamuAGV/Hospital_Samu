"""
Servicios para el módulo de Reportes
"""
from django.conf import settings
from datetime import datetime, timedelta
import pandas as pd
import json

db = getattr(settings, 'mongo_db', None)

class ReportService:
    """Servicios para reportes."""
    
    @staticmethod
    def generate_appointments_report(fecha_inicio=None, fecha_fin=None):
        """Generar reporte de citas."""
        if db is None:
            return None
        
        try:
            query = {}
            if fecha_inicio and fecha_fin:
                query['fecha_hora'] = {'$gte': fecha_inicio, '$lte': fecha_fin}
            
            appointments = list(db.appointments.find(query, {'_id': 0}))
            
            if appointments:
                df = pd.DataFrame(appointments)
                
                # Estadísticas
                stats = {
                    'total': len(df),
                    'por_estado': df['estado'].value_counts().to_dict() if 'estado' in df.columns else {},
                    'por_especialidad': df['especialidad'].value_counts().to_dict() if 'especialidad' in df.columns else {},
                }
                
                return {
                    'data': appointments,
                    'stats': stats
                }
            
            return {'data': [], 'stats': {'total': 0}}
        except Exception as e:
            print(f"Error en generate_appointments_report: {e}")
            return None
    
    @staticmethod
    def generate_occupancy_report():
        """Generar reporte de ocupación."""
        if db is None:
            return None
        
        try:
            total_camas = 120
            ocupadas = db.hospitalizations.count_documents({'estado': 'Activa'})
            
            # Historial de ocupación (simulado con datos reales si existen)
            historico = []
            for i in range(7, 0, -1):
                fecha = datetime.now() - timedelta(days=i)
                # Buscar ocupación real de ese día
                count = db.hospitalizations.count_documents({
                    'fecha_ingreso': {'$lte': fecha.isoformat()},
                    '$or': [
                        {'fecha_alta': {'$gte': fecha.isoformat()}},
                        {'fecha_alta': None}
                    ]
                })
                historico.append({
                    'fecha': fecha.strftime('%Y-%m-%d'),
                    'ocupacion': round((count / total_camas) * 100, 1) if count > 0 else 0
                })
            
            return {
                'total_camas': total_camas,
                'camas_ocupadas': ocupadas,
                'porcentaje': round((ocupadas / total_camas) * 100, 1),
                'historico': historico
            }
        except Exception as e:
            print(f"Error en generate_occupancy_report: {e}")
            return None
"""
Servicios para el módulo de Consultas
"""
from django.conf import settings
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

db = getattr(settings, 'mongo_db', None)

class ConsultationService:
    """Servicios para consultas médicas."""
    
    @staticmethod
    def get_daily_stats():
        """Obtener estadísticas diarias de consultas."""
        if db is None:
            return None
        
        try:
            # Consultas del día
            today = datetime.now().date()
            today_start = datetime.combine(today, datetime.min.time())
            today_end = datetime.combine(today, datetime.max.time())
            
            today_count = db.consultations.count_documents({
                'fecha_hora': {'$gte': today_start.isoformat(), '$lte': today_end.isoformat()}
            })
            
            # Semana actual
            week_start = today - timedelta(days=today.weekday())
            week_count = db.consultations.count_documents({
                'fecha_hora': {'$gte': week_start.isoformat()}
            })
            
            return {
                'today': today_count,
                'week': week_count,
                'avg_daily': round(week_count / 7, 1) if week_count > 0 else 0
            }
        except Exception as e:
            print(f"Error en get_daily_stats: {e}")
            return None
    
    @staticmethod
    def get_consultations_by_patient(patient_id):
        """Obtener consultas de un paciente."""
        if db is None:
            return []
        
        try:
            consultations = list(db.consultations.find(
                {'id_paciente': patient_id},
                {'_id': 0}
            ).sort('fecha_hora', -1))
            return consultations
        except Exception as e:
            print(f"Error en get_consultations_by_patient: {e}")
            return []
    
    @staticmethod
    def get_consultation_summary(consultation_id):
        """Obtener resumen de una consulta."""
        if db is None:
            return None
        
        try:
            from bson import ObjectId
            consultation = db.consultations.find_one(
                {'_id': ObjectId(consultation_id)},
                {'_id': 0}
            )
            
            if consultation:
                # Obtener diagnósticos
                diagnostics = list(db.diagnostics.find(
                    {'id_consulta': consultation_id},
                    {'_id': 0}
                ))
                
                # Obtener tratamientos
                treatments = list(db.treatments.find(
                    {'id_consulta': consultation_id},
                    {'_id': 0}
                ))
                
                return {
                    'consultation': consultation,
                    'diagnostics': diagnostics,
                    'treatments': treatments
                }
            return None
        except Exception as e:
            print(f"Error en get_consultation_summary: {e}")
            return None
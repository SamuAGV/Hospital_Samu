"""
Servicios centrales del sistema.
"""
import pandas as pd
import numpy as np
from datetime import datetime
import re
import logging

logger = logging.getLogger(__name__)

class DataCleanerService:
    """Servicio de limpieza de datos (migrado de data_cleaner.py)"""
    
    @staticmethod
    def clean_patients(df):
        """Limpiar datos de pacientes."""
        df = df.copy()
        
        # Manejar valores nulos
        df['nombre'] = df['nombre'].fillna('Desconocido').str.title()
        df['apellido'] = df['apellido'].fillna('Desconocido').str.title()
        df['telefono'] = df['telefono'].fillna('No registrado')
        df['email'] = df['email'].fillna('no@email.com')
        df['genero'] = df['genero'].fillna('No especificado')
        
        # Calcular edad si existe fecha_nacimiento
        if 'fecha_nacimiento' in df.columns:
            df['fecha_nacimiento'] = pd.to_datetime(df['fecha_nacimiento'])
            df['edad'] = (datetime.now() - df['fecha_nacimiento']).dt.days // 365
        
        # Limpiar teléfonos
        df['telefono'] = df['telefono'].apply(lambda x: re.sub(r'[^0-9]', '', str(x)))
        
        return df
    
    @staticmethod
    def validate_csv(df, required_columns):
        """Validar que el CSV tenga las columnas requeridas."""
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Faltan columnas: {', '.join(missing_columns)}")
        return True
    
    @staticmethod
    def get_stats(df):
        """Obtener estadísticas del DataFrame."""
        stats = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'null_count': df.isnull().sum().to_dict(),
            'duplicates': df.duplicated().sum(),
            'columns': df.columns.tolist(),
            'dtypes': df.dtypes.astype(str).to_dict(),
        }
        return stats
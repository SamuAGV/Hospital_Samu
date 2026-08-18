"""
Servicios de Machine Learning
"""
import pandas as pd
import numpy as np
import joblib
import os
from django.conf import settings
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import logging

logger = logging.getLogger(__name__)

class MLService:
    """Servicio de Machine Learning."""
    
    def __init__(self):
        self.models_dir = os.path.join(settings.BASE_DIR, 'ml', 'modelos')
        self.models = {}
        self.scalers = {}
        self.load_models()
    
    def load_models(self):
        """Cargar modelos guardados."""
        try:
            # Modelos supervisados
            if os.path.exists(os.path.join(self.models_dir, 'clasificador.pkl')):
                self.models['clasificador'] = joblib.load(os.path.join(self.models_dir, 'clasificador.pkl'))
                logger.info("✅ Clasificador cargado")
            
            if os.path.exists(os.path.join(self.models_dir, 'regresor.pkl')):
                self.models['regresor'] = joblib.load(os.path.join(self.models_dir, 'regresor.pkl'))
                logger.info("✅ Regresor cargado")
            
            # Modelos no supervisados
            if os.path.exists(os.path.join(self.models_dir, 'kmeans.pkl')):
                self.models['kmeans'] = joblib.load(os.path.join(self.models_dir, 'kmeans.pkl'))
                logger.info("✅ K-Means cargado")
            
            # Scalers
            for name in ['clasificacion', 'regresion', 'clustering']:
                path = os.path.join(self.models_dir, f'scaler_{name}.pkl')
                if os.path.exists(path):
                    self.scalers[name] = joblib.load(path)
                    logger.info(f"✅ Scaler {name} cargado")
                    
        except Exception as e:
            logger.error(f"❌ Error cargando modelos: {e}")
    
    def predict_risk(self, edad, consultas_previas, imc, genero):
        """Predecir riesgo de reingreso."""
        if 'clasificador' not in self.models:
            return None
        
        try:
            # Preparar características
            genero_encoded = 0 if genero == 'Masculino' else 1
            features = np.array([[edad, consultas_previas, imc, consultas_previas * 2, genero_encoded]])
            
            # Escalar si existe scaler
            if 'clasificacion' in self.scalers:
                features = self.scalers['clasificacion'].transform(features)
            
            # Predecir
            riesgo = self.models['clasificador'].predict_proba(features)[0][1]
            return float(riesgo * 100)
            
        except Exception as e:
            logger.error(f"Error en predicción de riesgo: {e}")
            return None
    
    def predict_stay(self, edad, consultas_previas, imc):
        """Predecir días de estancia."""
        if 'regresor' not in self.models:
            return None
        
        try:
            features = np.array([[edad, consultas_previas, imc]])
            
            if 'regresion' in self.scalers:
                features = self.scalers['regresion'].transform(features)
            
            estancia = self.models['regresor'].predict(features)[0]
            return float(max(1, estancia))
            
        except Exception as e:
            logger.error(f"Error en predicción de estancia: {e}")
            return None

# Instancia global
ml_service = MLService()
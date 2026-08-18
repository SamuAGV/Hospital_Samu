"""
Script para migrar los modelos ML del proyecto Streamlit a Django.
"""
import os
import sys
import shutil
from pathlib import Path

# Agregar directorio base al path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from apps.machine_learning.services import ml_service

def migrate_models():
    """Migrar modelos existentes."""
    print("=" * 60)
    print("MIGRANDO MODELOS DE MACHINE LEARNING")
    print("=" * 60)
    
    # Directorios
    source_dir = BASE_DIR / 'ml' / 'modelos'
    target_dir = BASE_DIR / 'apps' / 'machine_learning' / 'modelos'
    
    # Crear directorio destino
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Archivos a migrar
    files = [
        'clasificador.pkl',
        'regresor.pkl',
        'kmeans.pkl',
        'scaler_clasificacion.pkl',
        'scaler_regresion.pkl',
        'scaler_clustering.pkl',
    ]
    
    for file in files:
        source = source_dir / file
        target = target_dir / file
        
        if source.exists():
            shutil.copy2(source, target)
            print(f"✅ Copiado: {file}")
        else:
            print(f"⚠️ No encontrado: {file}")
    
    print("\n" + "=" * 60)
    print("✅ Migración completada")
    print("=" * 60)

if __name__ == "__main__":
    migrate_models()
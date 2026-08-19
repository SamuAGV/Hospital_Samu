"""
Utilidades para acceder a MongoDB desde cualquier parte del proyecto
"""
from django.conf import settings

def get_db():
    """Obtener la conexión a MongoDB."""
    return getattr(settings, 'MONGO_DB', None)

def get_collection(name):
    """Obtener una colección de MongoDB."""
    db = get_db()
    if db is not None:
        return db[name]
    return None

def is_connected():
    """Verificar si MongoDB está conectado."""
    return getattr(settings, 'MONGO_CONNECTED', False)

def get_stats():
    """Obtener estadísticas de MongoDB."""
    if not is_connected():
        return None
    
    db = get_db()
    if db is None:
        return None
    
    collections = ['patients', 'doctors', 'specialties', 'appointments', 'consultations',
                   'hospitalizations', 'diagnostics', 'treatments', 'medicines', 'inventory', 'users']
    
    stats = {}
    for coll in collections:
        try:
            stats[coll] = db[coll].count_documents({})
        except:
            stats[coll] = 0
    
    return stats

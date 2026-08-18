# apps/core/context_processors.py
from django.conf import settings

def mongodb_status(request):
    """Context processor para verificar el estado de MongoDB."""
    return {
        'mongodb_connected': settings.MONGO_CONNECTED,
        'mongodb_name': settings.MONGO_DB_NAME if settings.MONGO_CONNECTED and settings.MONGO_DB is not None else None,
    }
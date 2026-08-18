from django.conf import settings

def mongodb_status(request):
    """Context processor para el estado de MongoDB."""
    return {
        'mongodb_connected': getattr(settings, 'MONGO_CONNECTED', False),
        'mongodb_name': getattr(settings, 'MONGO_DB_NAME', 'No conectado'),
    }
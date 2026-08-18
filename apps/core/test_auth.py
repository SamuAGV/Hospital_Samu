# apps/core/test_auth.py
from django.http import JsonResponse
from django.conf import settings
from apps.users.utils import hash_password
import logging

logger = logging.getLogger(__name__)

def test_auth(request):
    """Endpoint para probar autenticación directamente."""
    data = {
        'mongodb_connected': settings.MONGO_CONNECTED,
        'mongodb_db': str(settings.MONGO_DB),
        'auth_backends': settings.AUTHENTICATION_BACKENDS,
    }
    
    if request.method == 'POST':
        import json
        try:
            body = json.loads(request.body)
            username = body.get('username')
            password = body.get('password')
            
            # Probar conexión directa a MongoDB
            if settings.MONGO_CONNECTED and settings.MONGO_DB is not None:
                db = settings.MONGO_DB
                users_collection = db['users']
                
                # Buscar usuario
                user_data = users_collection.find_one({
                    '$or': [
                        {'username': username},
                        {'email': username}
                    ]
                })
                
                if user_data:
                    data['user_found'] = True
                    data['username'] = user_data.get('username')
                    data['email'] = user_data.get('email')
                    
                    # Verificar contraseña
                    hashed_input = hash_password(password)
                    stored_hash = user_data.get('password', '')
                    
                    data['hashed_input'] = hashed_input[:30] + '...'
                    data['stored_hash'] = stored_hash[:30] + '...'
                    data['hash_match'] = hashed_input == stored_hash
                    data['hash_length_input'] = len(hashed_input)
                    data['hash_length_stored'] = len(stored_hash)
                    
                    # Intentar autenticar con Django
                    from django.contrib.auth import authenticate
                    user = authenticate(request, username=username, password=password)
                    data['django_auth_result'] = user is not None
                    data['django_user'] = str(user) if user else None
                    
                else:
                    data['user_found'] = False
            else:
                data['error'] = 'MongoDB no conectado'
                
        except Exception as e:
            data['error'] = str(e)
            import traceback
            data['traceback'] = traceback.format_exc()
    
    return JsonResponse(data)
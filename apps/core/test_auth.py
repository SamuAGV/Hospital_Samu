# apps/core/test_auth.py
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from apps.users.utils import hash_password, verify_password
from django.contrib.auth import authenticate
import logging
import json

logger = logging.getLogger(__name__)

@csrf_exempt
def test_auth(request):
    """Endpoint para probar autenticación directamente."""
    data = {
        'mongodb_connected': settings.MONGO_CONNECTED,
        'mongodb_db': str(settings.MONGO_DB),
        'auth_backends': settings.AUTHENTICATION_BACKENDS,
        'method': request.method,
    }
    
    if request.method == 'POST':
        try:
            # Leer el body
            body = json.loads(request.body)
            username = body.get('username')
            password = body.get('password')
            
            data['username'] = username
            data['password_provided'] = password is not None
            
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
                    data['username_db'] = user_data.get('username')
                    data['email_db'] = user_data.get('email')
                    
                    # Verificar contraseña
                    hashed_input = hash_password(password)
                    stored_hash = user_data.get('password', '')
                    
                    data['hash_match'] = hashed_input == stored_hash
                    data['hash_length_input'] = len(hashed_input)
                    data['hash_length_stored'] = len(stored_hash)
                    data['hash_input_preview'] = hashed_input[:20] + '...'
                    data['hash_stored_preview'] = stored_hash[:20] + '...'
                    
                    # Intentar autenticar con Django
                    try:
                        user = authenticate(request, username=username, password=password)
                        data['django_auth_result'] = user is not None
                        data['django_user'] = str(user) if user else None
                    except Exception as e:
                        data['django_auth_error'] = str(e)
                        data['django_auth_result'] = False
                    
                    # Verificar con verify_password
                    data['verify_password_result'] = verify_password(password, stored_hash)
                    
                else:
                    data['user_found'] = False
                    # Listar usuarios para depuración
                    users_list = list(users_collection.find({}, {'username': 1, 'email': 1, '_id': 0}))
                    data['users_in_db'] = users_list
            else:
                data['error'] = 'MongoDB no conectado'
                
        except json.JSONDecodeError as e:
            data['error'] = f'Error al parsear JSON: {str(e)}'
        except Exception as e:
            data['error'] = str(e)
            import traceback
            data['traceback'] = traceback.format_exc()
    else:
        data['message'] = 'Envía una petición POST con username y password'
    
    return JsonResponse(data)
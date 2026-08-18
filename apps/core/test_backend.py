# apps/core/test_backend.py
from django.http import JsonResponse
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.conf import settings
import json
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
def test_backend(request):
    """Endpoint para probar el backend de autenticación paso a paso."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        body = json.loads(request.body)
        username = body.get('username')
        password = body.get('password')
        
        result = {
            'username': username,
            'backend_path': settings.AUTHENTICATION_BACKENDS,
            'mongodb_connected': settings.MONGO_CONNECTED,
        }
        
        # PASO 1: Verificar conexión a MongoDB
        if not settings.MONGO_CONNECTED or settings.MONGO_DB is None:
            result['step1'] = '❌ MongoDB no conectado'
            return JsonResponse(result)
        
        db = settings.MONGO_DB
        users_collection = db['users']
        
        # PASO 2: Buscar usuario en MongoDB
        user_data = users_collection.find_one({
            '$or': [{'username': username}, {'email': username}]
        })
        
        if not user_data:
            result['step2'] = '❌ Usuario no encontrado en MongoDB'
            return JsonResponse(result)
        
        result['step2'] = f'✅ Usuario encontrado: {user_data.get("username")}'
        result['user_data'] = {
            'username': user_data.get('username'),
            'email': user_data.get('email'),
            'has_password': bool(user_data.get('password')),
            'is_superuser': user_data.get('is_superuser', False),
        }
        
        # PASO 3: Verificar contraseña (usando el mismo método que el backend)
        from apps.users.utils import verify_password
        stored_password = user_data.get('password', '')
        
        if not stored_password:
            result['step3'] = '❌ Usuario sin contraseña en MongoDB'
            return JsonResponse(result)
        
        password_valid = verify_password(password, stored_password)
        result['step3'] = f'✅ Contraseña válida: {password_valid}'
        result['password_valid'] = password_valid
        
        if not password_valid:
            return JsonResponse(result)
        
        # PASO 4: Intentar obtener/crear usuario de Django
        try:
            user = User.objects.get(username=user_data['username'])
            result['step4'] = f'✅ Usuario Django encontrado: {user.username}'
            result['django_user_found'] = True
            result['django_user'] = {
                'username': user.username,
                'email': user.email,
                'is_active': user.is_active,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
                'id': user.id,
                'has_usable_password': user.has_usable_password(),
            }
        except User.DoesNotExist:
            result['step4'] = f'🆕 Usuario Django NO existe, intentando crear...'
            result['django_user_found'] = False
            
            try:
                user = User(
                    username=user_data['username'],
                    email=user_data.get('email', ''),
                    first_name=user_data.get('first_name', ''),
                    last_name=user_data.get('last_name', ''),
                    is_active=user_data.get('is_active', True),
                    is_staff=user_data.get('is_staff', False),
                    is_superuser=user_data.get('is_superuser', False),
                )
                user.set_unusable_password()
                user.save()
                result['step4'] += f' ✅ Usuario Django creado: {user.username}'
                result['django_user_created'] = True
                result['django_user'] = {
                    'username': user.username,
                    'email': user.email,
                    'is_active': user.is_active,
                    'is_staff': user.is_staff,
                    'is_superuser': user.is_superuser,
                    'id': user.id,
                }
            except Exception as e:
                result['step4'] += f' ❌ Error al crear usuario Django: {str(e)}'
                result['django_user_created'] = False
                result['error'] = str(e)
                return JsonResponse(result)
        
        # PASO 5: Intentar autenticar con Django
        try:
            auth_user = authenticate(request, username=username, password=password)
            result['step5'] = f'✅ Django authenticate: {auth_user is not None}'
            result['django_auth_result'] = auth_user is not None
            
            if auth_user:
                result['django_auth_user'] = {
                    'username': auth_user.username,
                    'id': auth_user.id,
                    'is_active': auth_user.is_active,
                }
            else:
                # Si falla, probar manualmente
                try:
                    manual_user = User.objects.get(username=username)
                    result['manual_check'] = {
                        'user_exists': True,
                        'username': manual_user.username,
                        'is_active': manual_user.is_active,
                    }
                except User.DoesNotExist:
                    result['manual_check'] = {
                        'user_exists': False,
                        'message': 'El usuario no existe en la base de datos de Django'
                    }
                
        except Exception as e:
            result['step5'] = f'❌ Error en authenticate: {str(e)}'
            result['error'] = str(e)
        
        # PASO 6: Listar todos los usuarios de Django
        try:
            all_users = list(User.objects.all().values('username', 'email', 'is_active'))
            result['all_django_users'] = all_users
        except Exception as e:
            result['all_django_users_error'] = str(e)
        
        return JsonResponse(result)
        
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'traceback': __import__('traceback').format_exc()
        }, status=500)
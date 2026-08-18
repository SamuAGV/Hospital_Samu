# apps/core/test_login.py
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def test_login(request):
    """Endpoint para probar login manual."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        body = json.loads(request.body)
        username = body.get('username')
        password = body.get('password')
        
        # Intentar autenticar
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return JsonResponse({
                'success': True,
                'username': user.username,
                'is_authenticated': user.is_authenticated,
                'user_id': user.id
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Credenciales incorrectas'
            }, status=401)
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
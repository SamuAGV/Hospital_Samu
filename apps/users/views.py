# apps/users/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.models import User
import hashlib
import re
from datetime import datetime
import logging
logger = logging.getLogger(__name__)


def login_view(request):
    """Vista de inicio de sesión."""
    logger.info("=" * 50)
    logger.info("Vista de login iniciada")
    logger.info(f"Usuario autenticado: {request.user.is_authenticated}")
    
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        logger.info(f"Intento de login para usuario: {username}")
        logger.info(f"MONGO_CONNECTED: {settings.MONGO_CONNECTED}")
        logger.info(f"MONGO_DB: {settings.MONGO_DB}")
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            logger.info(f"Login exitoso para: {username}")
            messages.success(request, f'¡Bienvenido {user.username}!')
            return redirect('core:dashboard')
        else:
            logger.warning(f"Login fallido para: {username}")
            messages.error(request, 'Usuario o contraseña incorrectos')
    
    return render(request, 'users/login.html')


def register_view(request):
    """Vista de registro de nuevos usuarios."""
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        
        # Validaciones
        errors = []
        
        if not username or len(username) < 3:
            errors.append('El usuario debe tener al menos 3 caracteres')
        
        if not email or '@' not in email:
            errors.append('Email inválido')
        
        if not password or len(password) < 6:
            errors.append('La contraseña debe tener al menos 6 caracteres')
        
        if password != password2:
            errors.append('Las contraseñas no coinciden')
        
        # Verificar conexión a MongoDB - CORREGIDO
        if settings.MONGO_CONNECTED and settings.MONGO_DB is not None:
            db = settings.MONGO_DB
            users_collection = db['users']
            
            # Verificar si el usuario ya existe
            if users_collection.find_one({'username': username}):
                errors.append('El nombre de usuario ya está registrado')
            
            if users_collection.find_one({'email': email}):
                errors.append('El email ya está registrado')
        else:
            errors.append('No se pudo conectar a la base de datos')
        
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'users/register.html', {
                'username': username,
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
            })
        
        # Crear usuario en MongoDB
        try:
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            
            user_data = {
                'username': username,
                'email': email,
                'password': hashed_password,
                'first_name': first_name,
                'last_name': last_name,
                'is_active': True,
                'is_staff': False,
                'is_superuser': False,
                'date_joined': datetime.now().isoformat(),
                'last_login': None,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
            }
            
            db = settings.MONGO_DB
            users_collection = db['users']
            result = users_collection.insert_one(user_data)
            
            if result.inserted_id:
                messages.success(request, '¡Registro exitoso! Ahora puedes iniciar sesión.')
                return redirect('users:login')
            else:
                messages.error(request, 'Error al registrar usuario')
                
        except Exception as e:
            messages.error(request, f'Error al registrar: {str(e)}')
    
    return render(request, 'users/register.html')

def logout_view(request):
    """Vista de cierre de sesión."""
    logout(request)
    messages.info(request, 'Sesión cerrada correctamente')
    return redirect('users:login')

@login_required
def settings_view(request):
    """Vista de configuración de usuario."""
    context = {
        'page_title': 'Configuración',
        'user': request.user,
    }
    return render(request, 'users/settings.html', context)

@login_required
def profile_view(request):
    """Vista de perfil de usuario."""
    # Obtener datos adicionales de MongoDB
    user_extra = {}
    if settings.MONGO_CONNECTED and settings.MONGO_DB is not None:
        db = settings.MONGO_DB
        users_collection = db['users']
        user_data = users_collection.find_one({'username': request.user.username})
        if user_data:
            user_extra = user_data
    
    context = {
        'page_title': 'Mi Perfil',
        'user': request.user,
        'user_extra': user_extra,
    }
    return render(request, 'users/profile.html', context)

@login_required
def update_profile_view(request):
    """Vista para actualizar el perfil del usuario."""
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        email = request.POST.get('email', '')
        
        # Validaciones
        errors = []
        if not email or '@' not in email:
            errors.append('Email inválido')
        
        if errors:
            for error in errors:
                messages.error(request, error)
            return redirect('users:profile')
        
        if settings.MONGO_CONNECTED and settings.MONGO_DB is not None:
            db = settings.MONGO_DB
            users_collection = db['users']
            
            # Verificar si el email ya está en uso por otro usuario
            existing_user = users_collection.find_one({
                'email': email,
                'username': {'$ne': request.user.username}
            })
            if existing_user:
                messages.error(request, 'Este email ya está registrado por otro usuario')
                return redirect('users:profile')
            
            update_data = {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'updated_at': datetime.now().isoformat(),
            }
            
            result = users_collection.update_one(
                {'username': request.user.username},
                {'$set': update_data}
            )
            
            if result.modified_count > 0 or result.matched_count > 0:
                # Actualizar también el usuario de Django
                request.user.first_name = first_name
                request.user.last_name = last_name
                request.user.email = email
                request.user.save()
                
                messages.success(request, 'Perfil actualizado correctamente')
            else:
                messages.info(request, 'No se realizaron cambios')
        else:
            messages.error(request, 'No se pudo conectar a la base de datos')
        
        return redirect('users:profile')
    
    return redirect('users:profile')

@login_required
def change_password_view(request):
    """Vista para cambiar la contraseña."""
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        errors = []
        
        if not current_password:
            errors.append('Debes ingresar tu contraseña actual')
        
        if not new_password or len(new_password) < 6:
            errors.append('La nueva contraseña debe tener al menos 6 caracteres')
        
        if new_password != confirm_password:
            errors.append('Las contraseñas no coinciden')
        
        if settings.MONGO_CONNECTED and settings.MONGO_DB is not None:
            db = settings.MONGO_DB
            users_collection = db['users']
            
            user_data = users_collection.find_one({'username': request.user.username})
            if user_data:
                current_hashed = hashlib.sha256(current_password.encode()).hexdigest()
                if user_data.get('password') != current_hashed:
                    errors.append('La contraseña actual es incorrecta')
        
        if errors:
            for error in errors:
                messages.error(request, error)
            return redirect('users:settings')
        
        # Actualizar contraseña en MongoDB
        if settings.MONGO_CONNECTED and settings.MONGO_DB is not None:
            db = settings.MONGO_DB
            users_collection = db['users']
            
            new_hashed = hashlib.sha256(new_password.encode()).hexdigest()
            
            result = users_collection.update_one(
                {'username': request.user.username},
                {'$set': {
                    'password': new_hashed,
                    'updated_at': datetime.now().isoformat()
                }}
            )
            
            if result.modified_count > 0:
                messages.success(request, 'Contraseña actualizada correctamente')
            else:
                messages.error(request, 'Error al actualizar la contraseña')
        
        return redirect('users:settings')
    
    return redirect('users:settings')
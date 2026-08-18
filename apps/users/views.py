from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.models import User

def login_view(request):
    """Vista de inicio de sesión."""
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'¡Bienvenido {user.username}!')
            return redirect('core:dashboard')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    
    return render(request, 'users/login.html')

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
    context = {
        'page_title': 'Mi Perfil',
        'user': request.user,
    }
    return render(request, 'users/profile.html', context)
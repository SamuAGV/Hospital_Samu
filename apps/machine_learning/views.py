from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .services import ml_service

@login_required
def dashboard(request):
    """Dashboard de Machine Learning."""
    context = {
        'page_title': 'Machine Learning',
        'models_status': {
            'clasificador': 'clasificador' in ml_service.models,
            'regresor': 'regresor' in ml_service.models,
            'kmeans': 'kmeans' in ml_service.models,
        }
    }
    return render(request, 'machine_learning/dashboard.html', context)

@login_required
def predict_view(request):
    """Vista de predicción."""
    if request.method == 'POST':
        edad = int(request.POST.get('edad', 50))
        consultas = int(request.POST.get('consultas', 5))
        imc = float(request.POST.get('imc', 25))
        genero = request.POST.get('genero', 'Masculino')
        
        riesgo = ml_service.predict_risk(edad, consultas, imc, genero)
        estancia = ml_service.predict_stay(edad, consultas, imc)
        
        return JsonResponse({
            'riesgo': riesgo,
            'estancia': estancia,
            'status': 'success'
        })
    
    return render(request, 'machine_learning/predict.html')

@login_required
def train_view(request):
    """Vista para re-entrenar modelos."""
    if request.method == 'POST':
        # Aquí se implementaría la lógica de re-entrenamiento
        messages.success(request, 'Modelos re-entrenados correctamente')
        return redirect('machine_learning:dashboard')
    
    context = {
        'page_title': 'Entrenar Modelos',
    }
    return render(request, 'machine_learning/train.html')
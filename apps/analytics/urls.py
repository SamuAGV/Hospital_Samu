from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    # Eliminar o comentar estas líneas si no existen las funciones
    # path('heatmap/', views.heatmap_view, name='heatmap'),
    # path('demand/', views.demand_forecast, name='demand_forecast'),
]
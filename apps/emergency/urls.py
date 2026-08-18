from django.urls import path
from . import views

app_name = 'emergency'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('register/', views.register_patient, name='register'),
    path('<str:emergency_id>/', views.emergency_detail, name='detail'),
    path('stats/', views.emergency_stats, name='stats'),
]
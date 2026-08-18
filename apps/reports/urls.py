from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('appointments/', views.appointments_report, name='appointments'),
    path('consultations/', views.consultations_report, name='consultations'),
    path('occupancy/', views.occupancy_report, name='occupancy'),
    path('ml/', views.ml_report, name='ml_report'),
    path('export/<str:report_type>/', views.export_report, name='export'),
]
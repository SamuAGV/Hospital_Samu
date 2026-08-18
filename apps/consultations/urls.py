from django.urls import path
from . import views

app_name = 'consultations'

urlpatterns = [
    path('', views.list_consultations, name='list'),
    path('create/', views.create_consultation, name='create'),
    path('<str:consultation_id>/', views.consultation_detail, name='detail'),
    path('<str:consultation_id>/edit/', views.edit_consultation, name='edit'),
    path('<str:consultation_id>/diagnostic/', views.add_diagnostic, name='add_diagnostic'),
    path('<str:consultation_id>/treatment/', views.add_treatment, name='add_treatment'),
    path('stats/', views.consultation_stats, name='stats'),
]
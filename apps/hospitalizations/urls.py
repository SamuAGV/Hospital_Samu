from django.urls import path
from . import views

app_name = 'hospitalizations'

urlpatterns = [
    path('', views.list_hospitalizations, name='list'),
    path('create/', views.create_hospitalization, name='create'),
    path('<str:hospitalization_id>/', views.hospitalization_detail, name='detail'),
    path('<str:hospitalization_id>/discharge/', views.discharge_patient, name='discharge'),
    path('occupancy/', views.occupancy_view, name='occupancy'),
]
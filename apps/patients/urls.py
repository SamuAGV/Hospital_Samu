from django.urls import path
from . import views

app_name = 'patients'

urlpatterns = [
    path('', views.list_patients, name='list'),
    path('create/', views.create_patient, name='create'),
    path('<str:patient_id>/', views.patient_detail, name='detail'),
    path('<str:patient_id>/edit/', views.edit_patient, name='edit'),
    path('<str:patient_id>/delete/', views.delete_patient, name='delete'),
    path('search/', views.search_patients, name='search'),
]
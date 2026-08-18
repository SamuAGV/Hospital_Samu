from django.urls import path
from . import views

app_name = 'pharmacy'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('medicines/', views.list_medicines, name='list_medicines'),
    path('medicines/create/', views.create_medicine, name='create_medicine'),
    path('medicines/<str:medicine_id>/', views.medicine_detail, name='medicine_detail'),
    path('inventory/', views.inventory_view, name='inventory'),
    path('inventory/add/', views.add_inventory, name='add_inventory'),
    path('alerts/', views.alerts_view, name='alerts'),
]
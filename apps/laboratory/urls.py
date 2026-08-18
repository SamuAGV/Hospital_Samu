from django.urls import path
from . import views

app_name = 'laboratory'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('request/', views.create_request, name='create_request'),
    path('<str:request_id>/', views.request_detail, name='request_detail'),
    path('<str:request_id>/result/', views.add_result, name='add_result'),
    path('stats/', views.lab_stats, name='stats'),
]
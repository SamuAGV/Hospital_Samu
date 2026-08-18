from django.urls import path
from . import views

app_name = 'specialties'

urlpatterns = [
    path('', views.list_specialties, name='list'),
    path('create/', views.create_specialty, name='create'),
]
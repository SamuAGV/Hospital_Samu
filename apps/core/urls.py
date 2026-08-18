from django.urls import path
from . import views

# Usar un nombre de app específico
app_name = 'core'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('test-mongodb/', views.test_mongodb, name='test_mongodb'),

]
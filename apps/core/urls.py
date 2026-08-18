from django.urls import path
from . import views
from .test_auth import test_auth
from .test_backend import test_backend


# Usar un nombre de app específico
app_name = 'core'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('test-mongodb/', views.test_mongodb, name='test_mongodb'),
    path('test-auth/', test_auth, name='test_auth'),
    path('test-backend/', test_backend, name='test_backend'),



]
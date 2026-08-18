from django.urls import path
from . import views

app_name = 'machine_learning'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('predict/', views.predict_view, name='predict'),
    path('train/', views.train_view, name='train'),
]
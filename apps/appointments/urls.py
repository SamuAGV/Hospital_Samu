from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('', views.list_appointments, name='list'),
    path('create/', views.create_appointment, name='create'),
    path('<str:appointment_id>/', views.appointment_detail, name='detail'),
    path('<str:appointment_id>/cancel/', views.cancel_appointment, name='cancel'),
    path('<str:appointment_id>/reschedule/', views.reschedule_appointment, name='reschedule'),
    path('availability/', views.check_availability, name='availability'),
]
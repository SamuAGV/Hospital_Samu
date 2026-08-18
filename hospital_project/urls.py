from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),
    path('dashboard/', include('apps.core.urls')),
    path('patients/', include('apps.patients.urls')),
    path('appointments/', include('apps.appointments.urls')),
    path('consultations/', include('apps.consultations.urls')),
    path('hospitalizations/', include('apps.hospitalizations.urls')),
    path('emergency/', include('apps.emergency.urls')),
    path('laboratory/', include('apps.laboratory.urls')),
    path('pharmacy/', include('apps.pharmacy.urls')),
    path('specialties/', include('apps.specialties.urls')),
    path('analytics/', include('apps.analytics.urls')),
    path('ml/', include('apps.machine_learning.urls')),
    path('users/', include('apps.users.urls')),
    path('reports/', include('apps.reports.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
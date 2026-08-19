# hospital_project/wsgi.py
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_project.settings')

# Esta línea debe estar AL NIVEL MÁS ALTO, sin indentación
application = get_wsgi_application()
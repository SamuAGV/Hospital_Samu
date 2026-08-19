# hospital_project/wsgi.py
import os
import sys
import traceback
import logging

# Configurar logging básico para que salga en los logs de Vercel
logging.basicConfig(level=logging.DEBUG)

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_project.settings')

try:
    application = get_wsgi_application()
except Exception as e:
    # Esto imprimirá el error en los logs de Vercel para que podamos verlo
    print("=" * 80)
    print("ERROR FATAL AL INICIAR DJANGO EN VERCEL")
    print("=" * 80)
    traceback.print_exc(file=sys.stdout)
    print("=" * 80)
    # Re-lanzar la excepción para que Vercel sepa que falló
    raise
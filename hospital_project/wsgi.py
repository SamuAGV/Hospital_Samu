# hospital_project/wsgi.py
import os
import sys
import traceback

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_project.settings')

# La variable application DEBE estar DEFINIDA a nivel GLOBAL
try:
    application = get_wsgi_application()
except Exception as e:
    # Esto imprimirá el error en los logs de Vercel
    print("=" * 80)
    print("❌ ERROR AL CARGAR DJANGO EN VERCEL")
    print("=" * 80)
    traceback.print_exc(file=sys.stdout)
    print("=" * 80)
    
    # VERCEL espera que application esté definida. Si falla, definimos una dummy
    # para que Vercel no de error de "application not found", pero seguirá fallando
    # y el error real se verá en los logs.
    from django.http import HttpResponseServerError
    def application(environ, start_response):
        response = HttpResponseServerError(
            "Error en wsgi.py. Revisa los logs de Vercel."
        )
        return response(environ, start_response)
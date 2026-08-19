# apps/core/middleware.py
import logging
import traceback
from django.http import HttpResponseServerError

logger = logging.getLogger(__name__)

class ErrorLoggingMiddleware:
    """
    Middleware que captura cualquier excepción y la imprime en los logs
    para que Vercel la muestre.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        # Imprimir el error completo en los logs
        logger.error("=" * 80)
        logger.error(f"❌ ERROR 500 en {request.path}")
        logger.error(f"   Método: {request.method}")
        logger.error(f"   Usuario: {request.user}")
        logger.error("=" * 80)
        logger.error(traceback.format_exc())
        logger.error("=" * 80)
        
        # Opcional: devolver una respuesta 500 con el error (solo en DEBUG)
        return HttpResponseServerError(f"<pre>{traceback.format_exc()}</pre>")
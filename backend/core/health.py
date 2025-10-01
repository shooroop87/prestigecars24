# backend/core/health.py
import logging

from django.http import JsonResponse
from django.urls import path
from django.views.decorators.http import require_GET

logger = logging.getLogger(__name__)


@require_GET
def health(_request):
    # Liveness: просто факт, что процесс жив и принимает HTTP
    logger.info("💚 /health ping")
    return JsonResponse({"status": "ok"}, status=200)


urlpatterns = [
    path("health/", health),
]

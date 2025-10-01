import os
from pathlib import Path

from django.conf import settings
from django.core.wsgi import get_wsgi_application

# from whitenoise import WhiteNoise

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

BASE_DIR = Path(__file__).resolve().parent.parent

application = get_wsgi_application()

# # Простая настройка WhiteNoise
# if settings.DEBUG:
#     # В DEBUG режиме без кеширования
#     application = WhiteNoise(
#         application,
#         root=str(BASE_DIR / "collected_static"),
#         autorefresh=True,
#         max_age=0,
#     )
# else:
#     # В PRODUCTION режиме с коротким кешем
#     application = WhiteNoise(
#         application,
#         root=str(BASE_DIR / "collected_static"),
#         max_age=3600,  # 1 час вместо года
#     )

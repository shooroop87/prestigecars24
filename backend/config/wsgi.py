import os
from pathlib import Path

from django.conf import settings
from django.core.wsgi import get_wsgi_application

# from whitenoise import WhiteNoise

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

BASE_DIR = Path(__file__).resolve().parent.parent

application = get_wsgi_application()

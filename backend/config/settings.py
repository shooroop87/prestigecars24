# config/settings.py - ИСПРАВЛЕНА СТРУКТУРА ШАБЛОНОВ
import io
import os
import sys
from pathlib import Path

from django.utils.translation import gettext_lazy as _
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv("SECRET_KEY", "1insecure1-1default1")

# DEBUG выключает все виды кэша и сжатия
DEBUG = True

# ALLOWED_HOSTS
if DEBUG:
    ALLOWED_HOSTS = ["*"]
else:
    ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost 127.0.0.1").split()

CSRF_TRUSTED_ORIGINS = [
    "https://*.abroadstours.com",
    "https://abroadstours.com",
    "http://localhost",
    "http://localhost:8000",
    "http://backend-1:8000",
    "http://127.0.0.1",
    "http://127.0.0.1:8000",
    "http://0.0.0.0:8000",
]

# Приложения
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "meta",
    "core",
]

# Dev-only apps
if DEBUG:
    INSTALLED_APPS += ["django_browser_reload"]

MIDDLEWARE = [
    "django.middleware.gzip.GZipMiddleware",
    "django.middleware.security.SecurityMiddleware",
    # "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
if DEBUG:
    MIDDLEWARE.append("django_browser_reload.middleware.BrowserReloadMiddleware")

ROOT_URLCONF = "config.urls"

TEMPLATES_DIR = BASE_DIR / "templates"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "core" / "templates",  # Основные шаблоны
            BASE_DIR / "templates",  # Общие шаблоны
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "core.context_processors.default_schema",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# PostgreSQL
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB", "abroadtours"),
        "USER": os.getenv("POSTGRES_USER", "abroadtours_user"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", ""),
        "PORT": int(os.getenv("DB_PORT", 5432)),
    }
}

DEFAULT_CHARSET = "utf-8"
FILE_CHARSET = "utf-8"

LANGUAGE_CODE = "en"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = [
    ("en", "English"),
    ("it", _("Italian")),
]

LOCALE_PATHS = [BASE_DIR / "core" / "locale"]

# Static & media
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "core" / "static"]
STATIC_ROOT = BASE_DIR / "collected_static"

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

FILE_UPLOAD_PERMISSIONS = 0o644  # rw-r--r--
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755  # rwxr-xr-x

# Создаем медиа-директорию если не существует
os.makedirs(MEDIA_ROOT, exist_ok=True)

# Filer / thumbnails
THUMBNAIL_HIGH_RESOLUTION = True
THUMBNAIL_QUALITY = 90
THUMBNAIL_PROCESSORS = (
    "easy_thumbnails.processors.colorspace",
    "easy_thumbnails.processors.autocrop",
    "easy_thumbnails.processors.scale_and_crop",
    "filer.thumbnail_processors.scale_and_crop_with_subject_location",
    "easy_thumbnails.processors.filters",
)

# Отключить строгий режи
# WHITENOISE_MANIFEST_STRICT = False

# Cache / static storages
if DEBUG:
    STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
    CACHES = {"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}}
else:
    # STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
    STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": os.getenv("REDIS_URL", "redis://redis:6379/1"),
            "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
        }
    }

# НОВОЕ: Настройки для принуждения обновления браузерного кеша
# STATIC_CACHE_CONTROL = "public, max-age=3600"  # 1 час вместо года

# Email
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("EMAIL_HOST", "your-smtp-server.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True").lower() == "true"
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "your-email@domain.com")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "your-password")
DEFAULT_FROM_EMAIL = "Abroads Tours <noreply@abroadstours.com>"
CONTACT_EMAIL = "abroadstour@gmail.com"

# Контакты
CONTACT_PHONE = "+39-339-2168555"
WHATSAPP_NUMBER = "393392168555"

# SendPulse
SENDPULSE_API_USER_ID = os.getenv("SENDPULSE_API_USER_ID", "your-user-id")
SENDPULSE_API_SECRET = os.getenv("SENDPULSE_API_SECRET", "your-secret")
SENDPULSE_ADDRESS_BOOK_ID = os.getenv("SENDPULSE_ADDRESS_BOOK_ID", "your-book-id")

# SEO / verification
GOOGLE_ANALYTICS_ID = os.getenv("GA_MEASUREMENT_ID", "GA_MEASUREMENT_ID")
YANDEX_METRICA_ID = os.getenv("YANDEX_METRICA_ID", "YOUR_YANDEX_ID")
BING_WEBMASTER_ID = os.getenv("BING_WEBMASTER_ID", "YOUR_BING_ID")
BING_UET_TAG = os.getenv("BING_UET_TAG", "YOUR_BING_UET_TAG")
GOOGLE_SITE_VERIFICATION = os.getenv("GOOGLE_SITE_VERIFICATION", "")
YANDEX_VERIFICATION = os.getenv("YANDEX_VERIFICATION", "")
BING_SITE_VERIFICATION = os.getenv("BING_SITE_VERIFICATION", "")


# Misc
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# stdout fix
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# Parler
PARLER_LANGUAGES = {
    None: (
        {"code": "en"},
        {"code": "it"},
    ),
    "default": {"fallbacks": ["en"], "hide_untranslated": False},
}

# Meta
THUMBNAIL_FORMAT = "WEBP"
THUMBNAIL_QUALITY = 85
THUMBNAIL_PRESERVE_FORMAT = False

PAGINATE_BY = 10

FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 15 * 1024 * 1024  # 15MB

ALLOWED_IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".gif", ".webp"]
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB

IMAGE_QUALITY = 85
MAX_IMAGE_WIDTH = 1200
MAX_IMAGE_HEIGHT = 1200

THUMBNAIL_ALIASES = {
    "": {
        "blog_featured": {"size": (1200, 630), "crop": True, "quality": 85},
        "blog_preview": {"size": (400, 300), "crop": True, "quality": 85},
        "blog_thumb": {"size": (150, 150), "crop": True, "quality": 80},
        "admin_thumb": {"size": (100, 75), "crop": True, "quality": 75},
    },
}

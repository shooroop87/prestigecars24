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
DEBUG = False

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
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    # 3rd party
    "easy_thumbnails",
    "filer",
    "mptt",
    "parler",
    "django_ckeditor_5",
    "taggit",
    "meta",
    # local apps
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
            BASE_DIR / "blog" / "templates",  # Шаблоны блога
            BASE_DIR / "tours" / "templates",  # Шаблоны туров
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
                "core.context_processors.tours_context",
                # добавляем context_processor блога если существует
                # "blog.context_processors.blog_context",
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
    ("fr", _("French")),
    ("de", _("German")),
    ("es", _("Spanish")),
    ("nl", _("Dutch")),
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

# hCaptcha
HCAPTCHA_SITEKEY = os.getenv("HCAPTCHA_SITEKEY", "your-site-key-here")
HCAPTCHA_SECRET = os.getenv("HCAPTCHA_SECRET", "your-secret-key-here")
HCAPTCHA_DEFAULT_CONFIG = {"theme": "light", "size": "normal"}

# Misc
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# stdout fix
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

LOGS_DIR = BASE_DIR / "logs"
os.makedirs(LOGS_DIR, exist_ok=True)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {"format": "{levelname} {asctime} {message}", "style": "{"},
        "detailed": {
            "format": "🐛 {levelname} [{asctime}] {name} {module}:{lineno} - {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "detailed",
        },
        "file_debug": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": LOGS_DIR / "debug.log",
            "formatter": "detailed",
        },
        "media_file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": LOGS_DIR / "media.log",
            "formatter": "detailed",
        },
        "blog_file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": LOGS_DIR / "blog.log",
            "formatter": "detailed",
        },
        "core_file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": LOGS_DIR / "core.log",
            "formatter": "detailed",
        },
        "reviews_file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": LOGS_DIR / "reviews.log",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "core.views": {
            "handlers": ["core_file", "console"],
            "level": "DEBUG",
            "propagate": False,
        },
        "blog": {
            "handlers": ["blog_file", "console"],
            "level": "DEBUG",
            "propagate": False,
        },
        "blog.models": {
            "handlers": ["blog_file", "console"],
            "level": "DEBUG",
            "propagate": False,
        },
        "django.core.files": {
            "handlers": ["media_file", "console"],
            "level": "DEBUG",
            "propagate": False,
        },
        "PIL": {
            "handlers": ["media_file", "console"],
            "level": "DEBUG",
            "propagate": False,
        },
        "ckeditor": {
            "handlers": ["media_file", "console"],
            "level": "DEBUG",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["file_debug", "console"],
            "level": "DEBUG",
            "propagate": False,
        },
        "django": {"handlers": ["file_debug"], "level": "INFO", "propagate": False},
        "services.multi_reviews_service": {
            "handlers": ["reviews_file", "console"],
            "level": "INFO",
            "propagate": True,
        },
    },
    "root": {"handlers": ["console"], "level": "INFO"},
}

# API ключи для отзывов
TRIPADVISOR_API_KEY = os.getenv("TRIPADVISOR_API_KEY", "")
TRIPADVISOR_LOCATION_ID = os.getenv(
    "TRIPADVISOR_LOCATION_ID", "24938712"
)  # БЕЗ префикса 'd'
GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY", "")
GOOGLE_PLACE_ID = os.getenv("GOOGLE_PLACE_ID", "")
REVIEWS_CACHE_TIMEOUT = int(os.getenv("REVIEWS_CACHE_TIMEOUT", 86400))

# Parler
PARLER_LANGUAGES = {
    None: (
        {"code": "en"},
        {"code": "fr"},
        {"code": "de"},
        {"code": "es"},
        {"code": "nl"},
    ),
    "default": {"fallbacks": ["en"], "hide_untranslated": False},
}

# ===================== DJANGO CKEDITOR 5 =====================

# Загрузка файлов
CKEDITOR_5_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"

# ВАЖНО: inline-изображения из редактора блога кладём сюда:
# /media/blog/content/...
CKEDITOR_5_UPLOAD_PATH = "blog/content/"

CKEDITOR_5_IMAGE_UPLOAD_ENABLED = True
CKEDITOR_5_FILE_UPLOAD_ENABLED = True
CKEDITOR_5_ALLOW_ALL_FILE_TYPES = False
CKEDITOR_5_UPLOAD_FILE_TYPES = [
    "jpeg",
    "jpg",
    "png",
    "gif",
    "webp",
    "pdf",
    "doc",
    "docx",
]

CKEDITOR_5_CONFIGS = {
    "default": {
        "toolbar": [
            "heading",
            "|",
            "bold",
            "italic",
            "underline",
            "strikethrough",
            "|",
            "fontColor",
            "fontBackgroundColor",
            "|",
            "link",
            "uploadImage",
            "insertImage",
            "imageGallery",
            "blockQuote",
            "|",
            "bulletedList",
            "numberedList",
            "|",
            "outdent",
            "indent",
            "|",
            "insertTable",
            "|",
            "sourceEditing",
            "|",
            "undo",
            "redo",
        ],
        "fontColor": {
            "colors": [
                {"color": "hsl(0, 0%, 0%)", "label": "Black"},
                {"color": "hsl(0, 0%, 30%)", "label": "Dark grey"},
                {"color": "hsl(0, 0%, 60%)", "label": "Grey"},
                {"color": "hsl(0, 0%, 90%)", "label": "Light grey"},
                {"color": "hsl(0, 0%, 100%)", "label": "White", "hasBorder": True},
                {"color": "hsl(0, 75%, 60%)", "label": "Red"},
                {"color": "hsl(30, 75%, 60%)", "label": "Orange"},
                {"color": "hsl(60, 75%, 60%)", "label": "Yellow"},
                {"color": "hsl(90, 75%, 60%)", "label": "Light green"},
                {"color": "hsl(120, 75%, 60%)", "label": "Green"},
                {"color": "hsl(150, 75%, 60%)", "label": "Aquamarine"},
                {"color": "hsl(180, 75%, 60%)", "label": "Turquoise"},
                {"color": "hsl(210, 75%, 60%)", "label": "Light blue"},
                {"color": "hsl(240, 75%, 60%)", "label": "Blue"},
                {"color": "hsl(270, 75%, 60%)", "label": "Purple"},
                {"color": "hsl(300, 75%, 60%)", "label": "Magenta"},
                {"color": "hsl(330, 75%, 60%)", "label": "Pink"},
            ],
            "columns": 6,
        },
        "fontBackgroundColor": {
            "colors": [
                {"color": "hsl(0, 0%, 0%)", "label": "Black"},
                {"color": "hsl(0, 0%, 30%)", "label": "Dark grey"},
                {"color": "hsl(0, 0%, 60%)", "label": "Grey"},
                {"color": "hsl(0, 0%, 90%)", "label": "Light grey"},
                {"color": "hsl(0, 0%, 100%)", "label": "White", "hasBorder": True},
                {"color": "hsl(0, 75%, 60%)", "label": "Red"},
                {"color": "hsl(30, 75%, 60%)", "label": "Orange"},
                {"color": "hsl(60, 75%, 60%)", "label": "Yellow"},
                {"color": "hsl(90, 75%, 60%)", "label": "Light green"},
                {"color": "hsl(120, 75%, 60%)", "label": "Green"},
                {"color": "hsl(150, 75%, 60%)", "label": "Aquamarine"},
                {"color": "hsl(180, 75%, 60%)", "label": "Turquoise"},
                {"color": "hsl(210, 75%, 60%)", "label": "Light blue"},
                {"color": "hsl(240, 75%, 60%)", "label": "Blue"},
                {"color": "hsl(270, 75%, 60%)", "label": "Purple"},
                {"color": "hsl(300, 75%, 60%)", "label": "Magenta"},
                {"color": "hsl(330, 75%, 60%)", "label": "Pink"},
            ],
            "columns": 6,
        },
        "heading": {
            "options": [
                {
                    "model": "paragraph",
                    "view": {"name": "p", "classes": ["mt-20"]},
                    "title": "Paragraph",
                    "class": "ck-heading_paragraph",
                },
                {
                    "model": "heading1",
                    "view": {"name": "h1"},
                    "title": "Heading 1",
                    "class": "ck-heading_heading1",
                },
                {
                    "model": "heading2",
                    "view": {"name": "h2", "classes": ["text-30", "md:text-24"]},
                    "title": "Heading 2",
                    "class": "ck-heading_heading2",
                },
                {
                    "model": "heading3",
                    "view": {"name": "h3"},
                    "title": "Heading 3",
                    "class": "ck-heading_heading3",
                },
            ]
        },
        "image": {
            "toolbar": [
                "toggleImageCaption",
                "imageTextAlternative",
                "|",
                "linkImage",
                "|",
                "imageStyle:inline",
                "imageStyle:block",
                "imageStyle:side",
                "imageStyle:alignLeft",
                "imageStyle:alignRight",
                "resizeImage",
                "|",
                "imageGallery",
            ],
            "styles": [
                "inline",
                "block",
                "side",
                "alignLeft",
                "alignRight",
            ],
            "gallery": {
                "styles": ["inline", "block", "side"],
                "toolbar": [
                    "toggleImageCaption",
                    "imageTextAlternative",
                    "imageGallery",
                ],
                "resizeOptions": [
                    {
                        "name": "resizeImage:original",
                        "value": None,
                        "label": "Original",
                    },
                    {"name": "resizeImage:50", "value": "50", "label": "50%"},
                    {"name": "resizeImage:75", "value": "75", "label": "75%"},
                ],
            },
        },
        "table": {
            "contentToolbar": [
                "tableColumn",
                "tableRow",
                "mergeTableCells",
                "tableProperties",  # Свойства таблицы
                "tableCellProperties",  # Свойства ячеек
            ],
            "tableProperties": {
                "borderColors": [
                    {"color": "hsl(0, 0%, 90%)", "label": "Light gray"},
                    {"color": "hsl(0, 0%, 60%)", "label": "Gray"},
                    {"color": "hsl(0, 0%, 30%)", "label": "Dark gray"},
                ],
                "backgroundColors": [
                    {"color": "hsl(0, 0%, 100%)", "label": "White"},
                    {"color": "hsl(0, 0%, 95%)", "label": "Light gray"},
                    {"color": "hsl(210, 100%, 95%)", "label": "Light blue"},
                ],
            },
            "tableCellProperties": {
                "borderColors": [
                    {"color": "hsl(0, 0%, 90%)", "label": "Light gray"},
                    {"color": "hsl(0, 0%, 60%)", "label": "Gray"},
                ],
                "backgroundColors": [
                    {"color": "hsl(0, 0%, 100%)", "label": "White"},
                    {"color": "hsl(0, 0%, 95%)", "label": "Light gray"},
                ],
            },
        },
        "sourceEditing": {"allowCollaborationFeatures": True},
        "imageUpload": {
            "types": ["jpeg", "png", "gif", "bmp", "webp", "tiff"],
            "allowMultipleFiles": True,
        },
        "htmlSupport": {
            "allow": [
                {
                    "name": "figure",
                    "classes": [
                        "table",
                        "table-responsive",
                        "image-gallery",
                        "gallery-item",
                        "media",
                    ],
                },
                {
                    "name": "img",
                    "classes": ["gallery-image"],
                    "attributes": {"data-gallery": True},
                },
                {
                    "name": "table",
                    "classes": [
                        "compact",
                        "striped",
                        "lake-como-table",
                        "table-normal",
                    ],
                },
                {
                    "name": "div",
                    "classes": [
                        "table-responsive",
                        "table-stack",
                        "stack-item",
                        "image-gallery",
                        "gallery-grid",
                    ],
                },
                {
                    "name": "span",
                    "classes": ["stack-label", "stack-value", "stack-header"],
                },
                {"name": "td", "attributes": {"data-label": True}},
                {"name": "th", "attributes": {"data-label": True}},
                {"name": "h2", "classes": ["text-30", "md:text-24"]},
                {"name": "p", "classes": ["mt-20"]},
                {"name": "ul", "classes": ["list-disc", "mt-20"]},
                {"name": "ol", "classes": ["numbered-list", "mt-20"]},
            ],
            "disallow": [
                {"name": "p", "styles": {"margin-left": True, "padding-left": True}},
                {"name": "h1", "styles": {"margin-left": True, "padding-left": True}},
                {"name": "h2", "styles": {"margin-left": True, "padding-left": True}},
                {"name": "h3", "styles": {"margin-left": True, "padding-left": True}},
                {"name": "h4", "styles": {"margin-left": True, "padding-left": True}},
                {"name": "h5", "styles": {"margin-left": True, "padding-left": True}},
                {"name": "h6", "styles": {"margin-left": True, "padding-left": True}},
                {"name": "div", "styles": {"margin-left": True, "padding-left": True}},
                {"name": "ul", "styles": {"margin-left": True, "padding-left": True}},
                {"name": "ol", "styles": {"margin-left": True, "padding-left": True}},
                {"name": "li", "styles": {"margin-left": True, "padding-left": True}},
                {
                    "name": "blockquote",
                    "styles": {"margin-left": True, "padding-left": True},
                },
                {
                    "name": "/.*/",
                    "styles": {
                        "color": True,
                        "background": True,
                        "background-color": True,
                    },
                },
                {
                    "name": "span",
                    "styles": {
                        "color": True,
                        "background": True,
                        "background-color": True,
                    },
                },
            ],
        },
        "extraPlugins": ["ImageGallery", "ImageResize", "ImageUpload"],
    },
    # Профиль для блога с WordPress‑подобными стилями
    "blog": {
        "removePlugins": ["Indent", "IndentBlock"],
        "toolbar": [
            "heading",
            "|",
            "bold",
            "italic",
            "underline",
            "strikethrough",
            "removeFormat",
            "|",
            "fontColor",
            "fontBackgroundColor",
            "|",
            "bulletedList",
            "numberedList",
            "outdent",
            "indent",
            "|",
            "link",
            "blockQuote",
            "|",
            "uploadImage",
            "insertTable",
            "|",
            "style",
            "mediaEmbed",
            "|",
            "sourceEditing",
            "|",
            "undo",
            "redo",
        ],
        "fontColor": {
            "colors": [
                {"color": "hsl(0, 0%, 0%)", "label": "Black"},
                {"color": "hsl(0, 0%, 30%)", "label": "Dark grey"},
                {"color": "hsl(0, 0%, 60%)", "label": "Grey"},
                {"color": "hsl(0, 0%, 90%)", "label": "Light grey"},
                {"color": "hsl(0, 0%, 100%)", "label": "White", "hasBorder": True},
                {"color": "hsl(0, 75%, 60%)", "label": "Red"},
                {"color": "hsl(30, 75%, 60%)", "label": "Orange"},
                {"color": "hsl(60, 75%, 60%)", "label": "Yellow"},
                {"color": "hsl(90, 75%, 60%)", "label": "Light green"},
                {"color": "hsl(120, 75%, 60%)", "label": "Green"},
                {"color": "hsl(150, 75%, 60%)", "label": "Aquamarine"},
                {"color": "hsl(180, 75%, 60%)", "label": "Turquoise"},
                {"color": "hsl(210, 75%, 60%)", "label": "Light blue"},
                {"color": "hsl(240, 75%, 60%)", "label": "Blue"},
                {"color": "hsl(270, 75%, 60%)", "label": "Purple"},
                {"color": "hsl(300, 75%, 60%)", "label": "Magenta"},
                {"color": "hsl(330, 75%, 60%)", "label": "Pink"},
            ],
            "columns": 6,
        },
        "fontBackgroundColor": {
            "colors": [
                {"color": "hsl(0, 0%, 0%)", "label": "Black"},
                {"color": "hsl(0, 0%, 30%)", "label": "Dark grey"},
                {"color": "hsl(0, 0%, 60%)", "label": "Grey"},
                {"color": "hsl(0, 0%, 90%)", "label": "Light grey"},
                {"color": "hsl(0, 0%, 100%)", "label": "White", "hasBorder": True},
                {"color": "hsl(0, 75%, 60%)", "label": "Red"},
                {"color": "hsl(30, 75%, 60%)", "label": "Orange"},
                {"color": "hsl(60, 75%, 60%)", "label": "Yellow"},
                {"color": "hsl(90, 75%, 60%)", "label": "Light green"},
                {"color": "hsl(120, 75%, 60%)", "label": "Green"},
                {"color": "hsl(150, 75%, 60%)", "label": "Aquamarine"},
                {"color": "hsl(180, 75%, 60%)", "label": "Turquoise"},
                {"color": "hsl(210, 75%, 60%)", "label": "Light blue"},
                {"color": "hsl(240, 75%, 60%)", "label": "Blue"},
                {"color": "hsl(270, 75%, 60%)", "label": "Purple"},
                {"color": "hsl(300, 75%, 60%)", "label": "Magenta"},
                {"color": "hsl(330, 75%, 60%)", "label": "Pink"},
            ],
            "columns": 6,
        },
        "heading": {
            "options": [
                {
                    "model": "paragraph",
                    "view": {"name": "p", "classes": ["mt-20"]},
                    "title": "Paragraph",
                    "class": "ck-heading_paragraph",
                },
                {
                    "model": "heading1",
                    "view": {"name": "h1"},
                    "title": "Heading 1",
                    "class": "ck-heading_heading1",
                },
                {
                    "model": "heading2",
                    "view": {"name": "h2", "classes": ["text-30", "md:text-24"]},
                    "title": "Heading 2",
                    "class": "ck-heading_heading2",
                },
                {
                    "model": "heading3",
                    "view": {"name": "h3"},
                    "title": "Heading 3",
                    "class": "ck-heading_heading3",
                },
                {
                    "model": "heading4",
                    "view": {"name": "h4"},
                    "title": "Heading 4",
                    "class": "ck-heading_heading4",
                },
                {
                    "model": "heading5",
                    "view": {"name": "h5"},
                    "title": "Heading 5",
                    "class": "ck-heading_heading5",
                },
                {
                    "model": "heading6",
                    "view": {"name": "h6"},
                    "title": "Heading 6",
                    "class": "ck-heading_heading6",
                },
            ]
        },
        "style": {
            "definitions": [
                {
                    "name": "Numbered list (mt-20)",
                    "element": "ol",
                    "classes": ["numbered-list", "mt-20"],
                }
            ]
        },
        "list": {"properties": {"styles": True, "startIndex": True, "reversed": True}},
        "image": {
            "toolbar": [
                "toggleImageCaption",
                "imageTextAlternative",
                "|",
                "linkImage",
                "|",
                "imageStyle:inline",
                "imageStyle:block",
                "imageStyle:side",
                "imageStyle:alignLeft",
                "imageStyle:alignRight",
                "resizeImage",
            ],
            "styles": ["inline", "block", "side", "alignLeft", "alignRight"],
        },
        "table": {
            "contentToolbar": [
                "tableColumn",
                "tableRow",
                "mergeTableCells",
                "tableProperties",  # Свойства таблицы
                "tableCellProperties",  # Свойства ячеек
            ],
            "tableProperties": {
                "borderColors": [
                    {"color": "hsl(0, 0%, 90%)", "label": "Light gray"},
                    {"color": "hsl(0, 0%, 60%)", "label": "Gray"},
                    {"color": "hsl(0, 0%, 30%)", "label": "Dark gray"},
                ],
                "backgroundColors": [
                    {"color": "hsl(0, 0%, 100%)", "label": "White"},
                    {"color": "hsl(0, 0%, 95%)", "label": "Light gray"},
                    {"color": "hsl(210, 100%, 95%)", "label": "Light blue"},
                ],
            },
            "tableCellProperties": {
                "borderColors": [
                    {"color": "hsl(0, 0%, 90%)", "label": "Light gray"},
                    {"color": "hsl(0, 0%, 60%)", "label": "Gray"},
                ],
                "backgroundColors": [
                    {"color": "hsl(0, 0%, 100%)", "label": "White"},
                    {"color": "hsl(0, 0%, 95%)", "label": "Light gray"},
                ],
            },
        },
        "editorConfig": {
            "content": {
                "styles": """
                /* ===== ИСПРАВЛЕНИЕ ОТСТУПОВ DJANGO ADMIN ===== */
                form .wide p, form .wide ul.errorlist, form .wide input + p.help, form .wide input + div.help {
                    margin-left: 0 !important;
                }
                .form-row.wide {
                    margin-left: 0 !important;
                    padding-left: 0 !important;
                }
                .form-row.field-content {
                    margin-left: 0 !important;
                }

                /* ===== ОСНОВНЫЕ СТИЛИ РЕДАКТОРА (WordPress-подобные) ===== */
                .ck-content {
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen-Sans, Ubuntu, Cantarell, "Helvetica Neue", sans-serif !important;
                    color: #32373c !important;
                    background: #fff !important;
                    text-align: left !important;
                    color-scheme: light;
                    font-size: 16px !important;
                    line-height: 1.6 !important;
                    padding: 20px 24px !important;
                }

                .ck-content p {
                    font-size: 16px !important;
                    color: #32373c !important;
                    margin: 0 0 1em 0 !important;
                    line-height: 1.6 !important;
                }
                .ck-content p.mt-20 { margin-top: 20px !important; }

                .ck-content ul, .ck-content ol {
                    margin: 1em 0 1em 0em!important;
                    padding: 0 !important;
                }
                .ck-content ul {
                    list-style-type: disc !important;
                    list-style-position: outside !important;
                }
                .ck-content ol {
                    list-style-type: decimal !important;
                    list-style-position: outside !important;
                }
                .ck-content li {
                    margin: 0.5em 0 !important;
                    padding: 0 !important;
                    color: #32373c !important;
                    line-height: 1.6 !important;
                }

                .ck-content h1, .ck-content h2, .ck-content h3, .ck-content h4, .ck-content h5, .ck-content h6 {
                    text-align: left !important;
                    color: #23282d !important;
                    font-weight: 600 !important;
                    margin: 1.5em 0 0.5em 0 !important;
                    line-height: 1.3 !important;
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen-Sans, Ubuntu, Cantarell, "Helvetica Neue", sans-serif !important;
                }
                .ck-content h1 { font-size: 2.2em !important; margin-top: 1em !important; }
                .ck-content h2 { font-size: 1.8em !important; }
                .ck-content h2.text-30 { font-size: 1.875em !important; }
                .ck-content h3 { font-size: 1.5em !important; }
                .ck-content h4 { font-size: 1.25em !important; }
                .ck-content h5 { font-size: 1.1em !important; }
                .ck-content h6 { font-size: 1em !important; font-weight: 700 !important; }

                .ck-content a { color: #0073aa !important; text-decoration: none !important; }
                .ck-content a:hover { color: #005177 !important; text-decoration: underline !important; }

                .ck-content blockquote {
                    border-left: 4px solid #0073aa !important;
                    margin: 1.5em 0 !important;
                    padding: 0 0 0 1em !important;
                    font-style: italic !important;
                    color: #666 !important;
                    background: none !important;
                }
                .ck-content blockquote p { margin: 0.5em 0 !important; }

                .ck-content img {
                    max-width: 100% !important;
                    height: auto !important;
                    border-radius: 4px !important;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
                    margin: 1em 0 !important;
                }

                .ck-content table {
                    border-collapse: collapse !important;
                    width: 100% !important;
                    margin: 1em 0 !important;
                    background: #fff !important;
                }
                .ck-content table td, .ck-content table th {
                    border: 1px solid #e1e1e1 !important;
                    padding: 8px 12px !important;
                    text-align: left !important;
                    vertical-align: top !important;
                }
                .ck-content table th {
                    background: #f9f9f9 !important;
                    font-weight: 600 !important;
                    color: #23282d !important;
                }

                .ck-content code {
                    background: #f1f1f1 !important;
                    color: #d63384 !important;
                    padding: 2px 4px !important;
                    border-radius: 3px !important;
                    font-family: "Monaco", "Consolas", "Liberation Mono", "Courier New", monospace !important;
                    font-size: 0.9em !important;
                }

                .ck-content .image-style-align-left { float: left !important; margin: 0 1em 1em 0 !important; }
                .ck-content .image-style-align-right { float: right !important; margin: 0 0 1em 1em !important; }
                .ck-content .image-style-align-center { display: block !important; margin: 0 auto !important; }
                .ck-content .image-style-side { float: right !important; margin: 0 0 1em 1em !important; max-width: 50% !important; }
                .ck-content .image-style-inline { display: inline !important; margin: 0 0.2em !important; }
                .ck-content .image-style-block { display: block !important; margin: 1em auto !important; }
                """
            }
        },
        "htmlSupport": {
            "allow": [
                {"name": "h2", "classes": ["text-30", "md:text-24"]},
                {"name": "p", "classes": ["mt-20"]},
                {"name": "ol", "classes": ["numbered-list", "mt-20"]},
                {
                    "name": "iframe",
                    "attributes": {
                        "src": True,
                        "width": True,
                        "height": True,
                        "title": True,
                        "frameborder": True,
                        "allow": True,
                        "allowfullscreen": True,
                        "referrerpolicy": True,
                        "loading": True,
                    },
                },
                {"name": "figure", "classes": ["media"]},
                {"name": "oembed", "attributes": {"url": True}},
                {"name": "pre"},
                {"name": "code", "classes": True, "attributes": True},
                {"name": "div", "classes": True, "attributes": True},
                {"name": "span", "classes": True, "attributes": {"style": True}},
            ],
            "disallow": [
                {"name": "p", "styles": {"margin-left": True, "padding-left": True}},
                {"name": "h1", "styles": {"margin-left": True, "padding-left": True}},
                {"name": "h2", "styles": {"margin-left": True, "padding-left": True}},
                {"name": "h3", "styles": {"margin-left": True, "padding-left": True}},
                {"name": "h4", "styles": {"margin-left": True, "padding-left": True}},
                {"name": "h5", "styles": {"margin-left": True, "padding-left": True}},
                {"name": "h6", "styles": {"margin-left": True, "padding-left": True}},
                {"name": "div", "styles": {"margin-left": True, "padding-left": True}},
                {"name": "ul", "styles": {"margin-left": True, "padding-left": True}},
                {"name": "ol", "styles": {"margin-left": True, "padding-left": True}},
                {"name": "li", "styles": {"margin-left": True, "padding-left": True}},
                {
                    "name": "blockquote",
                    "styles": {"margin-left": True, "padding-left": True},
                },
                {
                    "name": "/.*/",
                    "styles": {
                        "color": True,
                        "background": True,
                        "background-color": True,
                    },
                },
                {
                    "name": "span",
                    "styles": {
                        "color": True,
                        "background": True,
                        "background-color": True,
                    },
                },
            ],
        },
        "mediaEmbed": {"previewsInData": True},
    },
    # Новый профиль: tour (полностью аналогичен blog)
    "tour": {
        "toolbar": [
            "heading",
            "|",
            "bold",
            "italic",
            "underline",
            "strikethrough",
            "removeFormat",
            "|",
            "bulletedList",
            "numberedList",
            "outdent",
            "indent",
            "|",
            "link",
            "blockQuote",
            "|",
            "uploadImage",
            "insertTable",
            "|",
            "style",
            "mediaEmbed",
            "|",
            "sourceEditing",
            "|",
            "undo",
            "redo",
        ],
        "heading": {
            "options": [
                {
                    "model": "paragraph",
                    "view": {"name": "p", "classes": ["mt-20"]},
                    "title": "Paragraph",
                    "class": "ck-heading_paragraph",
                },
                {
                    "model": "heading1",
                    "view": {"name": "h1"},
                    "title": "Heading 1",
                    "class": "ck-heading_heading1",
                },
                {
                    "model": "heading2",
                    "view": {"name": "h2", "classes": ["text-30", "md:text-24"]},
                    "title": "Heading 2",
                    "class": "ck-heading_heading2",
                },
                {
                    "model": "heading3",
                    "view": {"name": "h3"},
                    "title": "Heading 3",
                    "class": "ck-heading_heading3",
                },
                {
                    "model": "heading4",
                    "view": {"name": "h4"},
                    "title": "Heading 4",
                    "class": "ck-heading_heading4",
                },
                {
                    "model": "heading5",
                    "view": {"name": "h5"},
                    "title": "Heading 5",
                    "class": "ck-heading_heading5",
                },
                {
                    "model": "heading6",
                    "view": {"name": "h6"},
                    "title": "Heading 6",
                    "class": "ck-heading_heading6",
                },
            ]
        },
        "style": {
            "definitions": [
                {
                    "name": "Numbered list (mt-20)",
                    "element": "ol",
                    "classes": ["numbered-list", "mt-20"],
                }
            ]
        },
        "list": {"properties": {"styles": True, "startIndex": True, "reversed": True}},
        "image": {
            "toolbar": [
                "toggleImageCaption",
                "imageTextAlternative",
                "|",
                "linkImage",
                "|",
                "imageStyle:inline",
                "imageStyle:block",
                "imageStyle:side",
                "imageStyle:alignLeft",
                "imageStyle:alignRight",
                "resizeImage",
            ],
            "styles": ["inline", "block", "side", "alignLeft", "alignRight"],
        },
        "table": {"contentToolbar": ["tableColumn", "tableRow", "mergeTableCells"]},
        "editorConfig": {
            "content": {
                "styles": """
                /* ===== ИСПРАВЛЕНИЕ ОТСТУПОВ DJANGO ADMIN ===== */
                form .wide p, form .wide ul.errorlist, form .wide input + p.help, form .wide input + div.help {
                    margin-left: 0 !important;
                }
                .form-row.wide {
                    margin-left: 0 !important;
                    padding-left: 0 !important;
                }
                .form-row.field-content {
                    margin-left: 0 !important;
                }

                /* ===== ОСНОВНЫЕ СТИЛИ РЕДАКТОРА (WordPress-подобные) ===== */
                .ck-content {
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen-Sans, Ubuntu, Cantarell, "Helvetica Neue", sans-serif !important;
                    color: #32373c !important;
                    background: #fff !important;
                    text-align: left !important;
                    color-scheme: light;
                    font-size: 16px !important;
                    line-height: 1.6 !important;
                    padding: 20px 24px !important;
                }

                .ck-content p {
                    font-size: 16px !important;
                    color: #32373c !important;
                    margin: 0 0 1em 0 !important;
                    line-height: 1.6 !important;
                }
                .ck-content p.mt-20 { margin-top: 20px !important; }

                .ck-content ul, .ck-content ol {
                    margin: 1em 0 1em 0em!important;
                    padding: 0 !important;
                }
                .ck-content ul {
                    list-style-type: disc !important;
                    list-style-position: outside !important;
                }
                .ck-content ol {
                    list-style-type: decimal !important;
                    list-style-position: outside !important;
                }
                .ck-content li {
                    margin: 0.5em 0 !important;
                    padding: 0 !important;
                    color: #32373c !important;
                    line-height: 1.6 !important;
                }

                .ck-content h1, .ck-content h2, .ck-content h3, .ck-content h4, .ck-content h5, .ck-content h6 {
                    text-align: left !important;
                    color: #23282d !important;
                    font-weight: 600 !important;
                    margin: 1.5em 0 0.5em 0 !important;
                    line-height: 1.3 !important;
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen-Sans, Ubuntu, Cantarell, "Helvetica Neue", sans-serif !important;
                }
                .ck-content h1 { font-size: 2.2em !important; margin-top: 1em !important; }
                .ck-content h2 { font-size: 1.8em !important; }
                .ck-content h2.text-30 { font-size: 1.875em !important; }
                .ck-content h3 { font-size: 1.5em !important; }
                .ck-content h4 { font-size: 1.25em !important; }
                .ck-content h5 { font-size: 1.1em !important; }
                .ck-content h6 { font-size: 1em !important; font-weight: 700 !important; }

                .ck-content a { color: #0073aa !important; text-decoration: none !important; }
                .ck-content a:hover { color: #005177 !important; text-decoration: underline !important; }

                .ck-content blockquote {
                    border-left: 4px solid #0073aa !important;
                    margin: 1.5em 0 !important;
                    padding: 0 0 0 1em !important;
                    font-style: italic !important;
                    color: #666 !important;
                    background: none !important;
                }
                .ck-content blockquote p { margin: 0.5em 0 !important; }

                .ck-content img {
                    max-width: 100% !important;
                    height: auto !important;
                    border-radius: 4px !important;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
                    margin: 1em 0 !important;
                }

                .ck-content table {
                    border-collapse: collapse !important;
                    width: 100% !important;
                    margin: 1em 0 !important;
                    background: #fff !important;
                }
                .ck-content table td, .ck-content table th {
                    border: 1px solid #e1e1e1 !important;
                    padding: 8px 12px !important;
                    text-align: left !important;
                    vertical-align: top !important;
                }
                .ck-content table th {
                    background: #f9f9f9 !important;
                    font-weight: 600 !important;
                    color: #23282d !important;
                }

                .ck-content code {
                    background: #f1f1f1 !important;
                    color: #d63384 !important;
                    padding: 2px 4px !important;
                    border-radius: 3px !important;
                    font-family: "Monaco", "Consolas", "Liberation Mono", "Courier New", monospace !important;
                    font-size: 0.9em !important;
                }

                .ck-content .image-style-align-left { float: left !important; margin: 0 1em 1em 0 !important; }
                .ck-content .image-style-align-right { float: right !important; margin: 0 0 1em 1em !important; }
                .ck-content .image-style-align-center { display: block !important; margin: 0 auto !important; }
                .ck-content .image-style-side { float: right !important; margin: 0 0 1em 1em !important; max-width: 50% !important; }
                .ck-content .image-style-inline { display: inline !important; margin: 0 0.2em !important; }
                .ck-content .image-style-block { display: block !important; margin: 1em auto !important; }
                """
            }
        },
        "htmlSupport": {
            "allow": [
                {"name": "h2", "classes": ["text-30", "md:text-24"]},
                {"name": "p", "classes": ["mt-20"]},
                {"name": "ol", "classes": ["numbered-list", "mt-20"]},
                {
                    "name": "iframe",
                    "attributes": {
                        "src": True,
                        "width": True,
                        "height": True,
                        "title": True,
                        "frameborder": True,
                        "allow": True,
                        "allowfullscreen": True,
                        "referrerpolicy": True,
                        "loading": True,
                    },
                },
                {"name": "figure", "classes": ["media"]},
                {"name": "oembed", "attributes": {"url": True}},
            ],
            "disallow": [
                {"name": "/^(p|h1|h2|h3|h4|h5|h6)$/", "attributes": {"style": True}},
                {
                    "name": "/.*/",
                    "styles": {
                        "color": True,
                        "background": True,
                        "background-color": True,
                    },
                },
                {
                    "name": "span",
                    "styles": {
                        "color": True,
                        "background": True,
                        "background-color": True,
                    },
                },
            ],
        },
        "mediaEmbed": {"previewsInData": True},
    },
}


# Теги / изображения / пагинация
TAGGIT_CASE_INSENSITIVE = True

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

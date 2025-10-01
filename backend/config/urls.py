# backend/config/urls.py - ПРОСТАЯ ВЕРСИЯ ДЛЯ 4-Х СТРАНИЧНОГО САЙТА

import os

from core.sitemaps import StaticViewSitemap
from core.views import subscribe_to_newsletter
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.http import HttpResponse
from django.urls import include, path, re_path
from django.views.decorators.http import require_GET

# --- Sitemap config ---
sitemaps = {
    "static": StaticViewSitemap,
}


# --- robots.txt ---
@require_GET
def robots_txt(request):
    lines = [
        "User-agent: *",
        "Allow: /",
        "",
        f"Sitemap: https://{request.get_host()}/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


# --- URLs без языкового префикса ---
urlpatterns = [
    # SEO файлы
    path("robots.txt", robots_txt, name="robots_txt"),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
]

# --- Основные маршруты сайта ---
urlpatterns += i18n_patterns(
    # Core приложение - все страницы сайта
    path("", include("core.urls")),
    prefix_default_language=False,
)

# === МЕДИА ФАЙЛЫ ===
# Проверяем и создаем медиа-директорию если не существует
if not os.path.exists(settings.MEDIA_ROOT):
    os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
    print(f"✅ Создана медиа-директория: {settings.MEDIA_ROOT}")

if settings.DEBUG:
    print("🐛 DEBUG=True: Настройка обслуживания медиа через Django...")
    from django.conf.urls.static import static

    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    if "django_browser_reload" in settings.INSTALLED_APPS:
        urlpatterns += [
            path("__reload__/", include("django_browser_reload.urls")),
        ]
else:
    print("🚀 PRODUCTION MODE: Настройка обслуживания медиа для production...")
    from django.views.static import serve

    urlpatterns += [
        re_path(
            r"^media/(?P<path>.*)$",
            serve,
            {"document_root": settings.MEDIA_ROOT},
        ),
    ]

print(f"🔧 Итого URL patterns: {len(urlpatterns)}")
print(f"🔧 DEBUG: {settings.DEBUG}")
print(f"🔧 MEDIA_URL: {settings.MEDIA_URL}")
print(f"🔧 MEDIA_ROOT: {settings.MEDIA_ROOT}")

# Обработчики ошибок
handler404 = "core.views.custom_404"
handler500 = "core.views.custom_500"
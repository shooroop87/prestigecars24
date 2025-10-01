# backend/config/urls.py - ИСПРАВЛЕННАЯ ВЕРСИЯ С ГИБКИМИ URL

import os

# Импорты из core приложения
from core.sitemaps import CompleteSitemap
from core.views import subscribe_to_newsletter
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.http import HttpResponse
from django.urls import include, path, re_path
from django.views.decorators.http import require_GET
from django.views.i18n import set_language

# Импорты для блога
try:
    from blog.feeds import AtomBlogFeed, BlogFeed
    from blog.sitemaps import BlogPostSitemap, CategorySitemap

    BLOG_AVAILABLE = True
except ImportError:
    BLOG_AVAILABLE = False

# --- Sitemap config ---
sitemaps = {
    "complete": CompleteSitemap,
}

if BLOG_AVAILABLE:
    sitemaps.update(
        {
            "blog_posts": BlogPostSitemap,
            "blog_categories": CategorySitemap,
        }
    )


# --- robots.txt ---
@require_GET
def robots_txt(request):
    lines = [
        "User-agent: *",
        "Allow: /",
        "",
        f"Sitemap: https://{request.get_host()}/sitemap.xml",
    ]
    if BLOG_AVAILABLE:
        lines.extend(
            [
                "",
                "# Blog RSS feeds",
                f"# RSS: https://{request.get_host()}/blog/feed/",
                f"# Atom: https://{request.get_host()}/blog/feed/atom/",
            ]
        )
    return HttpResponse("\n".join(lines), content_type="text/plain")


# --- URLs без языкового префикса ---
urlpatterns = [
    path("robots.txt", robots_txt, name="robots_txt"),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path("set-language/", set_language, name="set_language"),
    path("subscribe/", subscribe_to_newsletter, name="subscribe"),
    # Django admin
    path("admin/", admin.site.urls),
    path("", include("core.health")),  # даёт /health/
    path("ckeditor5/", include("django_ckeditor_5.urls")),  # ЭТО ОБЯЗАТЕЛЬНО!
    # Django-Filer маршруты
    path("filer/", include("filer.urls")),
]

# Добавляем RSS feeds для блога если доступны
if BLOG_AVAILABLE:
    urlpatterns.extend(
        [
            path("blog/feed/", BlogFeed(), name="blog_feed"),
            path("blog/feed/atom/", AtomBlogFeed(), name="blog_feed_atom"),
        ]
    )

# --- Языковые маршруты ---
urlpatterns += i18n_patterns(
    # Blog приложение - обрабатывается первым для /blog/ URL-ов
    path("blog/", include("blog.urls")),
    # TOURS приложение - НОВАЯ СТРУКТУРА
    path("tours/", include(("tours.urls", "tours"), namespace="tours")),
    # Core приложение - все остальные URL-ы включая главную страницу
    # ВАЖНО: Core должен быть ПОСЛЕДНИМ, так как там catch-all patterns
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

# Обработчики ошибок
handler404 = "core.views.custom_404"
handler500 = "core.views.custom_500"

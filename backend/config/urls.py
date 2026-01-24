# config/urls.py
import os

from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.i18n import set_language
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView
from core.sitemaps import StaticSitemap, CarSitemap

sitemaps = {
    'static': StaticSitemap,
    'cars': CarSitemap,
}

# --- URLs без языкового префикса ---
urlpatterns = [
    path("set-language/", set_language, name="set_language"),
    path("admin/", admin.site.urls),
    # Third-party apps
    path("tinymce/", include("tinymce.urls")),
    path("filer/", include("filer.urls")),
    path('', include('core.urls')),
    # SEO
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path("robots.txt", TemplateView.as_view(template_name="robots.txt", content_type="text/plain"), name="robots"),
]

# --- Языковые маршруты ---
urlpatterns += i18n_patterns(
    # Core pages
    path("", include("core.urls")),
    
    prefix_default_language=False,
)

# === STATIC & MEDIA FILES ===
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Django Browser Reload
    if "django_browser_reload" in settings.INSTALLED_APPS:
        urlpatterns += [
            path("__reload__/", include("django_browser_reload.urls")),
        ]
    
    # Debug Toolbar
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            path("__debug__/", include(debug_toolbar.urls)),
        ] + urlpatterns

handler404 = 'core.views.error_404'
handler500 = 'core.views.error_500'
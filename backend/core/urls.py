# backend/core/urls.py - С ПЕРЕАДРЕСОВКОЙ СТАРЫХ URL ТУРОВ
from django.urls import path
from django.views.generic import RedirectView

# НОВОЕ: импортируем views для туров
from tours.views import TourCategoryView, TourDetailView

from . import views

urlpatterns = [
    # Главная страница
    path("", views.index, name="index"),
    # Основные страницы
    path("contact/", views.contact, name="contact"),
    path("about/", views.about, name="about"),
    path("privacy-policy/", views.privacy_policy, name="privacy_policy"),
    # AJAX эндпоинты
    path("load-more-reviews/", views.load_more_reviews, name="load_more_reviews"),
    # === ПЕРЕАДРЕСОВКИ СО СТАРЫХ URL НА НОВЫЕ ===
    # Переадресовка с /tours/category-name/ на /category-name/
    # Например: /tours/como-tours/ -> /como-tours/
    path(
        "tours/<slug:slug>/",
        RedirectView.as_view(pattern_name="tour_category_root", permanent=True),
        name="tour_category_old_redirect",
    ),
    # Переадресовка с /tours/category-name/tour-name/ на /category-name/tour-name/
    # Например: /tours/wine-tours/barolo-tour/ -> /wine-tours/barolo-tour/
    path(
        "tours/<slug:category_slug>/<slug:slug>/",
        RedirectView.as_view(pattern_name="tour_detail_root", permanent=True),
        name="tour_detail_old_redirect",
    ),
    # Страницы туров (статичная страница для SEO) - БЕЗ префикса tours/
    # /tours/ - общая страница со всеми турами
    path("tours/", views.tours, name="tours"),
    # Отладка
    path("debug-blog/", views.debug_blog_view, name="debug_blog"),
    # === НОВЫЕ ДИНАМИЧЕСКИЕ URL ТУРОВ В КОРНЕ ===
    # ВАЖНО: эти паттерны должны быть в самом конце!
    # Категории туров в корне: /wine-tours/, /como-tours/ и т.д.
    path("<slug:slug>/", TourCategoryView.as_view(), name="tour_category_root"),
    # Конкретные туры в категориях: /wine-tours/barolo-tour/
    path(
        "<slug:category_slug>/<slug:slug>/",
        TourDetailView.as_view(),
        name="tour_detail_root",
    ),
]

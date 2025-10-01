# backend/core/views.py - УЛУЧШЕННАЯ ВЕРСИЯ С ОТЛАДКОЙ И ИСПРАВЛЕНИЯМИ
import json
import logging
import os

import requests

# ДОБАВЛЕНО: импортируем модель BlogPost, Review и Tour
from blog.models import BlogPost
from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import (
    FileResponse,
    Http404,
    HttpResponse,
    HttpResponseRedirect,
    JsonResponse,
)
from django.shortcuts import render
from django.utils import timezone
from django.utils.translation import activate
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.vary import vary_on_headers
from tours.models import Tour, TourCategory  # НОВОЕ: импорт туров

# ДОБАВЛЕНО: импортируем модель отзывов
from .models import Review
from .services.reviews_import_service import ReviewsImportService

# Настройка логгера для отладки
logger = logging.getLogger("core.views")

# --- SendPulse API ключи ---
SENDPULSE_CLIENT_ID = "your_client_id"
SENDPULSE_CLIENT_SECRET = "your_client_secret"
SENDPULSE_LIST_ID = "your_list_id"


def get_sendpulse_token():
    url = "https://api.sendpulse.com/oauth/access_token"
    data = {
        "grant_type": "client_credentials",
        "client_id": SENDPULSE_CLIENT_ID,
        "client_secret": SENDPULSE_CLIENT_SECRET,
    }
    res = requests.post(url, data=data)
    return res.json().get("access_token")


@csrf_exempt
def subscribe_to_newsletter(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            email = data.get("email")

            if not email:
                return JsonResponse({"message": "Email is required"}, status=400)

            token = get_sendpulse_token()
            if not token:
                return JsonResponse({"message": "Authorization error"}, status=500)

            url = (
                f"https://api.sendpulse.com/addressbooks/" f"{SENDPULSE_LIST_ID}/emails"
            )
            headers = {"Authorization": f"Bearer {token}"}
            payload = {"emails": [{"email": email}]}

            response = requests.post(url, headers=headers, json=payload)

            if response.status_code == 200:
                return JsonResponse({"message": "Successfully subscribed"})
            else:
                return JsonResponse({"message": "Subscription failed"}, status=400)

        except (
            json.JSONDecodeError,
            requests.exceptions.RequestException,
            KeyError,
            ValueError,
        ):
            return JsonResponse({"message": "Server error"}, status=500)

    return JsonResponse({"message": "Invalid request"}, status=405)


# --- ОБНОВЛЕННЫЙ AJAX ENDPOINT ДЛЯ ОТЗЫВОВ ИЗ БД ---
# ИСПРАВЛЕННАЯ ФУНКЦИЯ ДЛЯ AJAX ПОДГРУЗКИ
@csrf_exempt
def load_more_reviews(request):
    """AJAX для подгрузки отзывов из БД с правильной пагинацией"""
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        page = int(request.GET.get("page", 1))
        per_page = int(request.GET.get("per_page", 5))

        # Для первой страницы пропускаем 5 отзывов (они уже показаны)
        offset = 5 if page == 1 else 5 + (page - 2) * per_page

        logger.info(
            f"📄 Запрос отзывов: страница {page}, per_page {per_page}, offset {offset}"
        )

        # Получаем отзывы из БД с правильным offset
        reviews_queryset = Review.objects.filter(is_active=True).order_by(
            "-is_featured", "-review_date", "-created_at"
        )

        total_count = reviews_queryset.count()

        # Получаем отзывы для текущей страницы
        if page == 1:
            # Для первой загрузки берем отзывы с 6-го по 10-й (индексы 5-9)
            reviews = reviews_queryset[5:10]
        else:
            # Для остальных страниц используем стандартную пагинацию
            start_index = 5 + (page - 2) * per_page
            end_index = start_index + per_page
            reviews = reviews_queryset[start_index:end_index]

        # Преобразуем в формат для фронтенда
        reviews_data = []
        for review in reviews:
            reviews_data.append(
                {
                    "review_id": review.external_id,
                    "author_name": review.author_name,
                    "author_photo_url": review.author_photo_url or "",
                    "rating": review.rating,
                    "text": review.text,
                    "relative_time_description": review.relative_time_description,
                    "source": review.source,
                }
            )

        # Проверяем, есть ли еще отзывы
        loaded_so_far = 5 + (page - 1) * per_page  # 5 изначальных + загруженные
        has_next = loaded_so_far < total_count

        response_data = {
            "reviews": reviews_data,
            "page": page,
            "per_page": per_page,
            "total_reviews": total_count,
            "loaded_so_far": loaded_so_far,
            "has_next": has_next,
            "offset_used": offset,
            "sources_used": {
                "database": True,
                "google": reviews_queryset.filter(source="google").exists(),
                "tripadvisor": reviews_queryset.filter(source="tripadvisor").exists(),
            },
            "fetched_at": "from_database",
        }

        logger.info(f"✅ Отправлено {len(reviews_data)} отзывов, has_next: {has_next}")
        return JsonResponse(response_data)

    except (ValueError, TypeError, AttributeError) as e:
        logger.error(f"❌ Ошибка загрузки отзывов: {e}")
        return JsonResponse({"error": "Error loading reviews"}, status=500)
    except Exception as e:
        logger.error(f"❌ Критическая ошибка загрузки отзывов: {e}")
        return JsonResponse({"error": "Internal server error"}, status=500)


# --- УЛУЧШЕННАЯ ФУНКЦИЯ ДЛЯ ТУРОВ С ОТЛАДКОЙ ---
def get_tours_context():
    """Получает туры и категории из БД"""
    logger.info("🎯 Получаем динамический контекст туров")

    try:
        # Все опубликованные туры
        published_tours = (
            Tour.objects.filter(status="published")
            .select_related("category")
            .prefetch_related("translations", "category__translations")
            .order_by("-is_featured", "sort_order", "-created_at")
        )

        # Активные категории
        tour_categories = (
            TourCategory.objects.filter(is_active=True)
            .prefetch_related("translations")
            .order_by("sort_order")
        )

        # Featured туры (топ 6)
        featured_tours = published_tours.filter(is_featured=True)[:6]
        if featured_tours.count() < 12:
            additional = published_tours.exclude(is_featured=True)[
                : 12 - featured_tours.count()
            ]
            featured_tours = list(featured_tours) + list(additional)

        # Туры по категориям (по 4 в каждой)
        tours_by_category = {}
        for category in tour_categories:
            category_tours = published_tours.filter(category=category)[:4]
            tours_by_category[category] = category_tours

        # Туры без категории (для "All Tours")
        uncategorized_tours = published_tours.filter(category__isnull=True)[:4]

        context = {
            "tour_categories": tour_categories,
            "featured_tours": featured_tours,
            "tours_by_category": tours_by_category,
            "uncategorized_tours": uncategorized_tours,
            "all_tours": published_tours[:12],  # Топ 6 для "All Tours"
        }

        logger.info(
            f"✅ Контекст: {len(tour_categories)} категорий, {len(featured_tours)} featured"
        )
        return context

    except Exception as e:
        logger.error(f"❌ Ошибка get_tours_context: {e}")
        return {
            "tour_categories": [],
            "featured_tours": [],
            "tours_by_category": {},
            "uncategorized_tours": [],
            "all_tours": [],
        }


# --- ЯЗЫК ---
def set_language(request):
    lang = request.GET.get("language")
    next_url = request.GET.get("next", "/")
    if lang in dict(settings.LANGUAGES):
        activate(lang)
        response = HttpResponseRedirect(next_url)
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang)
        return response
    return HttpResponseRedirect("/")


# --- ГЛАВНАЯ СТРАНИЦА С ОТЗЫВАМИ ИЗ БД И ТУРАМИ ---
@cache_page(60 * 15)  # Кеширование на 15 минут
@vary_on_headers("Accept-Language")
def index(request):
    """
    Главная страница с последними статьями блога, отзывами из БД и турами.
    """
    logger.info("🏠 ===== Загрузка главной страницы =====")

    # Получаем последние 3 опубликованные статьи из BlogPost
    try:
        logger.info("📝 Получаем последние статьи блога...")
        latest_posts = (
            BlogPost.objects.filter(status="published")
            .select_related("category", "author")
            .prefetch_related("tags")
            .order_by("-published_at")[:3]
        )
        posts_count = latest_posts.count()
        logger.info(f"📝 Найдено статей блога: {posts_count}")

    except Exception as e:
        logger.error(f"❌ Ошибка получения статей блога: {e}")
        latest_posts = []

    # ИСПРАВЛЕНО: Получаем последние 50 отзывов из БД
    try:
        logger.info("⭐ Получаем последние 50 отзывов из БД...")

        # Получаем последние 50 отзывов для главной страницы
        db_reviews = Review.objects.filter(is_active=True).order_by(
            "-is_featured", "-review_date", "-created_at"
        )[
            :50
        ]  # ← ИЗМЕНЕНО: теперь 50 отзывов вместо 7

        # Преобразуем в формат для шаблона
        reviews_for_template = []
        for review in db_reviews:
            reviews_for_template.append(
                {
                    "review_id": review.external_id,
                    "author_name": review.author_name,
                    "author_photo_url": review.author_photo_url or "",
                    "rating": review.rating,
                    "text": review.text,
                    "relative_time_description": review.relative_time_description,
                    "source": review.source,
                }
            )

        # Проверяем есть ли еще отзывы для пагинации
        total_reviews = Review.objects.filter(is_active=True).count()
        has_next = total_reviews > 50  # ← ИЗМЕНЕНО: теперь проверяем на 50

        logger.info(
            f"⭐ Загружено отзывов из БД: {len(reviews_for_template)} из {total_reviews}"
        )

        reviews_data = {
            "reviews": reviews_for_template,
            "has_next": has_next,
            "page": 1,
            "total_reviews": total_reviews,
            "from_database": True,
            "sources_used": {
                "database": True,
                "google": Review.objects.filter(
                    source="google", is_active=True
                ).exists(),
                "tripadvisor": Review.objects.filter(
                    source="tripadvisor", is_active=True
                ).exists(),
            },
            "fetched_at": timezone.now().strftime("%b %d, %H:%M"),
        }

    except Exception as e:
        logger.error(f"❌ Ошибка получения отзывов из БД: {e}")
        reviews_for_template = []
        reviews_data = {
            "reviews": [],
            "has_next": False,
            "page": 1,
            "total_reviews": 0,
            "from_database": False,
            "sources_used": {"database": False},
            "fetched_at": "Error",
        }

    # Получаем контекст туров
    logger.info("🎯 Получаем контекст туров...")
    tours_context = get_tours_context()

    all_tours = list(tours_context.get("all_tours", []))[:9]
    tours_context["all_tours"] = all_tours

    context = {
        "latest_posts": latest_posts,
        "reviews_data": reviews_data,
        "google_reviews": reviews_for_template,  # Для обратной совместимости
    }

    # Добавляем туры в контекст
    context.update(tours_context)

    logger.info(f"🏠 Итоговый контекст сформирован:")
    logger.info(f"   - Статей блога: {len(latest_posts)}")
    logger.info(f"   - Отзывов: {len(reviews_for_template)}")
    logger.info(f"   - Featured туров: {len(context.get('featured_tours', []))}")

    return render(request, "pages/index.html", context)


# --- ОСНОВНЫЕ СТРАНИЦЫ ---
@cache_page(60 * 60 * 24)
@vary_on_headers("Accept-Language")
def contact(request):
    logger.info("📞 Загрузка страницы контактов")
    context = get_tours_context()
    return render(request, "pages/contact.html", context)


@cache_page(60 * 60 * 24)
@vary_on_headers("Accept-Language")
def privacy_policy(request):
    logger.info("🔒 Загрузка страницы политики конфиденциальности")
    context = get_tours_context()
    return render(request, "pages/privacy_policy.html", context)


@cache_page(60 * 60 * 24)
@vary_on_headers("Accept-Language")
def about(request):
    logger.info("ℹ️ Загрузка страницы О нас")
    context = get_tours_context()
    return render(request, "pages/about.html", context)


# --- СТРАНИЦЫ КАТЕГОРИЙ ТУРОВ (СТАТИЧНЫЕ ДЛЯ SEO) ---
@cache_page(60 * 60 * 24)
@vary_on_headers("Accept-Language")
def tours(request):
    logger.info("🎯 Загрузка общей страницы туров")
    context = get_tours_context()
    return render(request, "pages/tour-list.html", context)


# --- КАСТОМНЫЕ ОШИБКИ ---
def custom_404(request, exception):
    logger.warning(f"404 ошибка: {request.path}")
    return render(request, "pages/404.html", status=404)


def custom_500(request):
    logger.error(f"500 ошибка на странице: {request.path}")
    return render(request, "pages/500.html", status=500)


def debug_blog_view(request):
    """Расширенная отладочная view для проверки всех компонентов системы"""
    if not settings.DEBUG:
        raise Http404("Debug mode only")

    logger.info("🐛 ===== НАЧАЛО ОТЛАДОЧНОЙ ПРОВЕРКИ =====")

    # Проверяем BlogPost
    try:
        logger.info("📝 Проверяем статьи блога...")
        latest_posts = BlogPost.objects.filter(status="published").order_by(
            "-published_at"
        )[:5]
        posts_info = []

        for post in latest_posts:
            try:
                title = post.get_display_title()
                url = post.get_absolute_url()
                posts_info.append(
                    {
                        "id": post.id,
                        "title": title,
                        "author": post.author.username,
                        "published_at": post.published_at,
                        "has_image": bool(post.featured_image),
                        "image_url": (
                            post.featured_image.url if post.featured_image else None
                        ),
                        "category": str(post.category) if post.category else None,
                        "url": url,
                        "status": "OK",
                    }
                )
                logger.debug(f"✅ Пост OK: '{title}' -> {url}")
            except Exception as e:
                posts_info.append({"id": post.id, "error": str(e), "status": "ERROR"})
                logger.error(f"❌ Ошибка поста ID={post.id}: {e}")

        logger.info(f"📝 Статей проверено: {len(posts_info)}")

    except Exception as e:
        posts_info = [{"error": str(e)}]
        logger.error(f"❌ Критическая ошибка проверки статей: {e}")

    # Проверяем отзывы
    try:
        logger.info("⭐ Проверяем отзывы...")
        reviews = Review.objects.filter(is_active=True)[:5]
        reviews_info = []

        for review in reviews:
            reviews_info.append(
                {
                    "id": review.id,
                    "external_id": review.external_id,
                    "source": review.source,
                    "author": review.author_name,
                    "rating": review.rating,
                    "text": (
                        review.text[:100] + "..."
                        if len(review.text) > 100
                        else review.text
                    ),
                    "is_featured": review.is_featured,
                    "review_date": review.review_date.isoformat(),
                    "relative_time": review.relative_time_description,
                }
            )

        # Статистика по отзывам
        reviews_stats = {
            "total": Review.objects.count(),
            "active": Review.objects.filter(is_active=True).count(),
            "featured": Review.objects.filter(is_featured=True).count(),
            "by_source": {
                source[0]: Review.objects.filter(
                    source=source[0], is_active=True
                ).count()
                for source in Review.SOURCE_CHOICES
            },
        }

        logger.info(f"⭐ Отзывов проверено: {len(reviews_info)}")

    except Exception as e:
        reviews_info = [{"error": str(e)}]
        reviews_stats = {"error": str(e)}
        logger.error(f"❌ Критическая ошибка проверки отзывов: {e}")

    # Проверяем туры (РАСШИРЕННАЯ ПРОВЕРКА)
    try:
        logger.info("🎯 Проверяем туры...")
        tours = Tour.objects.filter(status="published")[
            :10
        ]  # Больше туров для проверки
        tours_info = []

        for tour in tours:
            try:
                title = tour.safe_translation_getter("title", any_language=True)
                slug = tour.safe_translation_getter("slug", any_language=True)
                url = tour.get_absolute_url()

                tours_info.append(
                    {
                        "id": tour.id,
                        "title": title,
                        "slug": slug,
                        "location": tour.location,
                        "price_adult": float(tour.price_adult),
                        "duration_hours": tour.duration_hours,
                        "rating": float(tour.rating),
                        "reviews_count": tour.reviews_count,
                        "is_featured": tour.is_featured,
                        "category": (
                            tour.category.safe_translation_getter(
                                "name", any_language=True
                            )
                            if tour.category
                            else None
                        ),
                        "category_id": tour.category.id if tour.category else None,
                        "url": url,
                        "status": "OK" if title and url else "PROBLEM",
                        "has_translations": bool(tour.translations.exists()),
                    }
                )

                status = "OK" if title and url else "PROBLEM"
                logger.debug(
                    f"{'✅' if status == 'OK' else '⚠️'} Тур {tour.id}: '{title}' -> {url}"
                )

            except Exception as e:
                tours_info.append({"id": tour.id, "error": str(e), "status": "ERROR"})
                logger.error(f"❌ Ошибка тура ID={tour.id}: {e}")

        tours_stats = {
            "total": Tour.objects.count(),
            "published": Tour.objects.filter(status="published").count(),
            "featured": Tour.objects.filter(is_featured=True).count(),
            "categories": TourCategory.objects.filter(is_active=True).count(),
            "with_translations": Tour.objects.filter(translations__isnull=False)
            .distinct()
            .count(),
        }

        logger.info(f"🎯 Туров проверено: {len(tours_info)}")

    except Exception as e:
        tours_info = [{"error": str(e)}]
        tours_stats = {"error": str(e)}
        logger.error(f"❌ Критическая ошибка проверки туров: {e}")

    # Проверяем категории туров (НОВОЕ)
    try:
        logger.info("📂 Проверяем категории туров...")
        categories = TourCategory.objects.filter(is_active=True)
        categories_info = []

        for category in categories:
            try:
                name = category.safe_translation_getter("name", any_language=True)
                slug = category.safe_translation_getter("slug", any_language=True)
                url = category.get_absolute_url()
                tours_count = Tour.objects.filter(
                    category=category, status="published"
                ).count()

                categories_info.append(
                    {
                        "id": category.id,
                        "name": name,
                        "slug": slug,
                        "url": url,
                        "tours_count": tours_count,
                        "sort_order": category.sort_order,
                        "status": "OK" if name and url else "PROBLEM",
                        "has_translations": bool(category.translations.exists()),
                    }
                )

                status = "OK" if name and url else "PROBLEM"
                logger.debug(
                    f"{'✅' if status == 'OK' else '⚠️'} Категория {category.id}: '{name}' -> {url} ({tours_count} туров)"
                )

            except Exception as e:
                categories_info.append(
                    {"id": category.id, "error": str(e), "status": "ERROR"}
                )
                logger.error(f"❌ Ошибка категории ID={category.id}: {e}")

        logger.info(f"📂 Категорий проверено: {len(categories_info)}")

    except Exception as e:
        categories_info = [{"error": str(e)}]
        logger.error(f"❌ Критическая ошибка проверки категорий: {e}")

    # Проверяем структуру шаблонов
    try:
        logger.info("📄 Проверяем шаблоны...")
        import django
        from django.template.loader import get_template

        template_info = {}
        templates_to_check = [
            "pages/index.html",
            "mainpage/index.html",
            "core/mainpage/index.html",
            "index.html",
            "base.html",
            "blog/blog_list.html",
            "includes/header.html",
            "includes/header-tour.html",
            "includes/header-mobile-menu.html",
            "mainpage/tours.html",
            "includes/similar_experiences.html",
        ]

        for template_name in templates_to_check:
            try:
                template = get_template(template_name)
                template_info[template_name] = {
                    "found": True,
                    "origin": (
                        str(template.origin)
                        if hasattr(template, "origin")
                        else "unknown"
                    ),
                    "status": "OK",
                }
                logger.debug(f"✅ Шаблон найден: {template_name}")
            except Exception as e:
                template_info[template_name] = {
                    "found": False,
                    "error": str(e),
                    "status": "ERROR",
                }
                logger.warning(f"⚠️ Шаблон не найден: {template_name} - {e}")

        logger.info(f"📄 Шаблонов проверено: {len(template_info)}")

    except Exception as e:
        template_info = {"error": str(e)}
        logger.error(f"❌ Критическая ошибка проверки шаблонов: {e}")

    # Статус импорта отзывов
    try:
        logger.info("🔄 Проверяем статус импорта отзывов...")
        import_service = ReviewsImportService()
        import_status = import_service.get_import_status()
        logger.info("✅ Статус импорта получен")
    except Exception as e:
        import_status = {"error": str(e)}
        logger.error(f"❌ Ошибка получения статуса импорта: {e}")

    # Проверяем контекст туров (КРИТИЧЕСКАЯ ПРОВЕРКА)
    try:
        logger.info("🎯 Проверяем get_tours_context()...")
        tours_context_result = get_tours_context()

        tours_context_debug = {
            "status": "OK",
            "categories_count": len(tours_context_result.get("tour_categories", [])),
            "all_tours_count": len(tours_context_result.get("all_tours", [])),
            "featured_tours_count": len(tours_context_result.get("featured_tours", [])),
            "wine_tours_count": len(tours_context_result.get("wine_tours", [])),
            "como_tours_count": len(tours_context_result.get("como_tours", [])),
            "city_tours_count": len(tours_context_result.get("city_tours", [])),
        }

        # Проверяем каждый featured tour на корректность
        featured_tours_debug = []
        for i, tour in enumerate(tours_context_result.get("featured_tours", [])):
            try:
                title = tour.safe_translation_getter("title", any_language=True)
                url = tour.get_absolute_url()
                featured_tours_debug.append(
                    {
                        "index": i,
                        "id": tour.id,
                        "title": title,
                        "url": url,
                        "status": "OK" if title and url else "PROBLEM",
                    }
                )
            except Exception as e:
                featured_tours_debug.append(
                    {
                        "index": i,
                        "id": getattr(tour, "id", "unknown"),
                        "error": str(e),
                        "status": "ERROR",
                    }
                )

        tours_context_debug["featured_tours_debug"] = featured_tours_debug
        logger.info(
            f"🎯 Контекст туров проверен: {tours_context_debug['featured_tours_count']} featured туров"
        )

    except Exception as e:
        tours_context_debug = {"error": str(e), "status": "ERROR"}
        logger.error(f"❌ Критическая ошибка проверки контекста туров: {e}")

    # Формируем итоговые данные для отладки
    debug_data = {
        "timestamp": str(timezone.now()),
        "django_version": django.get_version(),
        "settings": {
            "DEBUG": settings.DEBUG,
            "TEMPLATES_DIRS": [str(path) for path in settings.TEMPLATES[0]["DIRS"]],
            "INSTALLED_APPS": settings.INSTALLED_APPS,
            "LANGUAGES": settings.LANGUAGES,
        },
        "blog_posts": {
            "data": posts_info,
            "count": len([p for p in posts_info if p.get("status") == "OK"]),
            "errors": len([p for p in posts_info if p.get("status") == "ERROR"]),
        },
        "reviews": {
            "data": reviews_info,
            "stats": reviews_stats,
            "import_status": import_status,
        },
        "tours": {
            "data": tours_info,
            "stats": tours_stats,
            "context_debug": tours_context_debug,
        },
        "categories": {
            "data": categories_info,
            "count": len([c for c in categories_info if c.get("status") == "OK"]),
            "errors": len([c for c in categories_info if c.get("status") == "ERROR"]),
        },
        "templates": template_info,
        "media_settings": {
            "MEDIA_URL": settings.MEDIA_URL,
            "MEDIA_ROOT": settings.MEDIA_ROOT,
            "media_root_exists": os.path.exists(settings.MEDIA_ROOT),
            "media_root_readable": (
                os.access(settings.MEDIA_ROOT, os.R_OK)
                if os.path.exists(settings.MEDIA_ROOT)
                else False
            ),
            "media_root_writable": (
                os.access(settings.MEDIA_ROOT, os.W_OK)
                if os.path.exists(settings.MEDIA_ROOT)
                else False
            ),
        },
        "system_health": {
            "tours_context_working": tours_context_debug.get("status") == "OK",
            "templates_found": len(
                [
                    t
                    for t in template_info.values()
                    if isinstance(t, dict) and t.get("found")
                ]
            ),
            "templates_missing": len(
                [
                    t
                    for t in template_info.values()
                    if isinstance(t, dict) and not t.get("found")
                ]
            ),
            "critical_issues": [],
        },
    }

    # Выявляем критические проблемы
    if tours_context_debug.get("status") != "OK":
        debug_data["system_health"]["critical_issues"].append("tours_context_failed")

    if debug_data["system_health"]["templates_missing"] > 0:
        debug_data["system_health"]["critical_issues"].append("missing_templates")

    if len([t for t in tours_info if t.get("status") == "ERROR"]) > 0:
        debug_data["system_health"]["critical_issues"].append("tour_processing_errors")

    logger.info("🐛 ===== ОТЛАДОЧНАЯ ПРОВЕРКА ЗАВЕРШЕНА =====")
    logger.info(
        f"🐛 Критических проблем: {len(debug_data['system_health']['critical_issues'])}"
    )

    if debug_data["system_health"]["critical_issues"]:
        logger.warning(
            f"⚠️ Найдены проблемы: {debug_data['system_health']['critical_issues']}"
        )
    else:
        logger.info("✅ Критических проблем не обнаружено")

    return JsonResponse(debug_data, indent=2)

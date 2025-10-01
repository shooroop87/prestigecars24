import json

from django.apps import apps
from django.core.exceptions import AppRegistryNotReady


def default_schema(request):
    schema = {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "name": "Abroads Tours",
        "alternateName": "Abroads Tours SRL",
        "description": (
            "Top-rated small group and private tours from Milan to Lake Como, "
            "Switzerland (Lugano), Barolo, and more. Escape the crowds and enjoy "
            "authentic experiences with expert guides."
        ),
        "image": "https://abroadstours.com/static/img/general/svgexport-1.svg",
        "url": "https://abroadstours.com",
        "telephone": ["+39 320 857 5909", "+39 339 216 8555"],
        "email": "abroadstour@gmail.com",
        "priceRange": "$$",
        "address": {
            "@type": "PostalAddress",
            "streetAddress": "Piazza Duca d'Aosta",
            "addressLocality": "Milan",
            "addressRegion": "Lombardy",
            "postalCode": "20124",
            "addressCountry": "IT",
        },
        "geo": {"@type": "GeoCoordinates", "latitude": 45.484, "longitude": 9.204},
        "openingHoursSpecification": [
            {
                "@type": "OpeningHoursSpecification",
                "dayOfWeek": [
                    "Monday",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday",
                    "Saturday",
                    "Sunday",
                ],
                "opens": "08:00",
                "closes": "23:00",
            }
        ],
        "founders": [
            {"@type": "Person", "name": "Oleg Danylyuk"},
            {
                "@type": "Person",
                "name": "Stefano Depaola",
                "telephone": ["+39 339 216 8555", "+39 320 857 5909"],
                "contactType": "owner",
                "areaServed": [
                    "Milan",
                    "Lake Como",
                    "Lugano",
                    "Barolo",
                    "Piedmont",
                    "Switzerland",
                    "Bellagio",
                    "Varenna",
                ],
                "availableLanguage": ["English", "Italian", "Spanish"],
            },
        ],
        "sameAs": [
            "https://www.instagram.com/abroads_tours/",
            "https://www.getyourguide.com/abroads-tours-srl-s269953/",
            "https://g.co/kgs/CwXz9sN",
            "https://www.tripadvisor.com/Attraction_Review-g187849-d24938712-Reviews-Abroads_Tours-Milan_Lombardy.html",
            "https://www.viator.com/tours/Milan/Varenna-Bellagio-and-villa-Balbianello-tour-from-Milan/d512-362653P1",
            "https://www.viator.com/tours/Milan/Best-of-Como-city-walking-tour-boat-cruise-and-ice-cream-tasting/d512-362653P4",
            "https://www.viator.com/tours/Milan/Barolo-wine-Tasting-Alba-and-Unesco-castle-visit-Small-group/d512-362653P5",
        ],
        "aggregateRating": {
            "@type": "AggregateRating",
            "ratingValue": "5.0",
            "reviewCount": "1500",
            "bestRating": "5",
            "worstRating": "1",
        },
        "review": {
            "@type": "Review",
            "reviewRating": {"@type": "Rating", "ratingValue": "5"},
            "author": {"@type": "Person", "name": "James"},
            "reviewBody": (
                "The Barolo wine tour was one of my favorite experiences in 5 weeks "
                "in Italy. Personal, authentic, and beautifully organized. Highly recommended!"
            ),
        },
    }
    return {"schema_json": json.dumps(schema, ensure_ascii=False)}


def tours_context(request):
    """Контекстный процессор для туров - ИСПРАВЛЕННЫЙ"""
    try:
        # Импортируем модели только когда они нужны
        from tours.models import Tour, TourCategory

        # Получаем активные категории туров
        tour_categories = TourCategory.objects.filter(is_active=True).order_by(
            "sort_order"
        )

        # Получаем все опубликованные туры
        all_tours = (
            Tour.objects.filter(status="published")
            .select_related("category")
            .order_by("-is_featured", "sort_order")[:10]
        )

        # Группируем туры по категориям
        tours_by_category = {}
        for category in tour_categories:
            category_tours = Tour.objects.filter(
                category=category, status="published"
            ).order_by("-is_featured", "sort_order")[:6]
            tours_by_category[category] = category_tours

        return {
            "tour_categories": tour_categories,
            "all_tours": all_tours,
            "tours_by_category": tours_by_category,
        }

    except (ImportError, AppRegistryNotReady):
        # Если приложение tours не готово или не установлено
        return {
            "tour_categories": [],
            "all_tours": [],
            "tours_by_category": {},
        }
    except Exception as e:
        # Логируем ошибку для отладки
        import logging

        logger = logging.getLogger("core.context_processors")
        logger.error(f"Ошибка в tours_context: {e}")

from django.shortcuts import render, get_object_or_404
from .models import Car, CarCategory
from django.views.decorators.vary import vary_on_headers
from django.views.decorators.cache import cache_page

from .models import Car


def index(request):
    """Главная страница с машинами из БД"""
    cars = Car.objects.filter(is_active=True).select_related('category')[:6]
    
    return render(request, "pages/index.html", {'cars': cars})


@cache_page(60 * 15)  # кешируем на 15 минут
@vary_on_headers("Accept-Language")
def privacy(request):
    return render(request, 'pages/privacy_policy.html')


@cache_page(60 * 15)  # кешируем на 15 минут
@vary_on_headers("Accept-Language")
def cookies(request):
    return render(request, 'pages/cookies.html')


@cache_page(60 * 15)  # кешируем на 15 минут
@vary_on_headers("Accept-Language")
def contacts(request):
    return render(request, 'pages/contacts.html')


@cache_page(60 * 15)  # кешируем на 15 минут
@vary_on_headers("Accept-Language")
def faq(request):
    return render(request, "pages/faq.html")


def car_detail(request, category_slug, car_slug):
    car = get_object_or_404(
        Car.objects.select_related('category'),
        slug=car_slug,
        category__slug=category_slug,
        is_active=True
    )
    return render(request, "pages/car_detail.html", {"car": car})


def car_list_by_category(request, category_slug):
    category = get_object_or_404(CarCategory, slug=category_slug)
    cars = Car.objects.filter(category=category, is_active=True)
    return render(request, "pages/car_list.html", {"category": category, "cars": cars})

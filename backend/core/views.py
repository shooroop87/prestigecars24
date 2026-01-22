from django.shortcuts import render, get_object_or_404
from .models import Car, CarCategory


def index(request):
    """Главная страница."""
    return render(request, "pages/index.html")


def privacy(request):
    return render(request, 'pages/privacy_policy.html')


def cookies(request):
    return render(request, 'pages/cookies.html')


def contacts(request):
    return render(request, 'pages/contacts.html')


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

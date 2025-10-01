# backend/core/views.py

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.conf import settings


@cache_page(60 * 60 * 24)
def home(request):
    """Главная страница"""
    return render(request, "pages/index.html")


@cache_page(60 * 60 * 24)
@vary_on_headers("Accept-Language")
def about(request):
    """Страница О нас"""
    return render(request, "pages/about.html")


@cache_page(60 * 60 * 24)
@vary_on_headers("Accept-Language")
def contact(request):
    """Страница Контакты"""
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")
        
        # Отправка email
        try:
            send_mail(
                subject=f"Контактная форма: {name}",
                message=message,
                from_email=email,
                recipient_list=[settings.DEFAULT_FROM_EMAIL],
                fail_silently=False,
            )
            return JsonResponse({"success": True, "message": "Сообщение отправлено!"})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})
    
    return render(request, "pages/contact.html")


def fleet(request):
    """Страница Автопарк"""
    # Здесь будет логика получения автомобилей из БД
    # vehicles = Vehicle.objects.filter(is_active=True)
    context = {
        # "vehicles": vehicles,
    }
    return render(request, "pages/fleet.html", context)


# Обработчики ошибок
def custom_404(request, exception):
    """Кастомная страница 404"""
    return render(request, "errors/404.html", status=404)


def custom_500(request):
    """Кастомная страница 500"""
    return render(request, "errors/500.html", status=500)
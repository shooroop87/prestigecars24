import os
import re
import socket
import requests
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.vary import vary_on_headers
from django.views.decorators.cache import cache_page

from .models import Car
from .services import send_telegram


# === ВАЛИДАЦИЯ ===

def validate_email(email):
    """Проверка email: формат + существование домена"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Invalid email format"
    
    domain = email.split('@')[1]
    try:
        socket.gethostbyname(domain)
        return True, None
    except socket.gaierror:
        return False, "Email domain does not exist"


def validate_phone(phone):
    """Проверка телефона: минимум 8 цифр"""
    digits = re.sub(r'\D', '', phone)
    if len(digits) < 8:
        return False, "Phone number too short"
    if len(digits) > 15:
        return False, "Phone number too long"
    return True, None

    
# === API ДЛЯ ФОРМ ===

@require_POST
def booking_request(request):
    """Hero форма бронирования"""
    location = request.POST.get('location', '')
    date = request.POST.get('date', '')
    time = request.POST.get('time', '')
    car_class = request.POST.get('car_class', '')
    dropoff = request.POST.get('dropoff', '')
    phone = request.POST.get('phone', '')
    
    # Валидация телефона
    is_valid, error = validate_phone(phone)
    if not is_valid:
        return JsonResponse({'success': False, 'error': error}, status=400)
    
    # Очищаем телефон для WhatsApp ссылки (только цифры)
    phone_clean = re.sub(r'\D', '', phone)
    
    # Telegram сообщение
    message = f"""🚗 <b>New Booking Request</b>

📍 Pickup: {location}
📍 Dropoff: {dropoff}
📅 Date: {date}
🕐 Time: {time}
🚘 Class: {car_class}
📱 Phone: <a href="https://wa.me/{phone_clean}">{phone}</a>"""
    
    send_telegram(message)
    
    return JsonResponse({'success': True, 'message': 'Thank you! We will contact you shortly.'})


@require_POST
def contact_request(request):
    """Контактная форма"""
    first_name = request.POST.get('first_name', '')
    last_name = request.POST.get('last_name', '')
    email = request.POST.get('email', '')
    phone = request.POST.get('phone', '')
    message_text = request.POST.get('message', '')
    source = request.POST.get('source', 'contact_page')
    
    # Валидация email
    if email:
        is_valid, error = validate_email(email)
        if not is_valid:
            return JsonResponse({'success': False, 'error': error}, status=400)
    
    # Валидация телефона
    if phone:
        is_valid, error = validate_phone(phone)
        if not is_valid:
            return JsonResponse({'success': False, 'error': error}, status=400)
    
    # Telegram сообщение
    message = f"""📩 <b>New Contact Request</b>

👤 Name: {first_name} {last_name}
📧 Email: {email}
📱 Phone: {phone}
📝 Source: {source}

💬 Message:
{message_text}"""
    
    send_telegram(message)
    
    return JsonResponse({'success': True, 'message': 'Thank you! We will get back to you soon.'})


# === СТРАНИЦЫ ===

def index(request):
    """Главная страница с машинами из БД"""
    cars = Car.objects.filter(is_active=True).select_related('category')[:6]
    return render(request, "pages/index.html", {'cars': cars})


@cache_page(60 * 15)
@vary_on_headers("Accept-Language")
def privacy(request):
    return render(request, 'pages/privacy_policy.html')


@cache_page(60 * 15)
@vary_on_headers("Accept-Language")
def cookies(request):
    return render(request, 'pages/cookies.html')


@cache_page(60 * 15)
@vary_on_headers("Accept-Language")
def contacts(request):
    return render(request, 'pages/contacts.html')


@cache_page(60 * 15)
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

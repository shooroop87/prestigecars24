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
    car_class = request.POST.get('car_class', '')
    dropoff = request.POST.get('dropoff', '')
    full_phone = request.POST.get('full_phone', '')
    email = request.POST.get('email', '').strip()
    
    # Валидация телефона
    if not full_phone or len(full_phone) < 8:
        return JsonResponse({'success': False, 'error': 'Invalid phone number'}, status=400)
    
    # Валидация email
    if not email:
        return JsonResponse({'success': False, 'error': 'Please enter your email'}, status=400)
    
    is_valid, error = validate_email(email)
    if not is_valid:
        return JsonResponse({'success': False, 'error': error}, status=400)
    
    wa_phone = re.sub(r'\D', '', full_phone)
    
    message = f"""🚗 <b>New Booking Request</b>

📍 Pickup: {location}
📍 Dropoff: {dropoff}
📅 Date: {date}
🚘 Class: {car_class}
📱 Phone: <a href="https://wa.me/{wa_phone}">{full_phone}</a>
📧 Email: {email}"""
    
    send_telegram(message)
    
    return JsonResponse({'success': True})


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

def error_404(request, exception):
    return render(request, '404.html', status=404)

def error_500(request):
    return render(request, '500.html', status=500)

@require_POST
def car_request(request):
    """Запрос на конкретную машину"""
    car_name = request.POST.get('car_name', '')
    car_url = request.POST.get('car_url', '')
    full_phone = request.POST.get('full_phone', '')
    email = request.POST.get('email', '').strip()
    date = request.POST.get('date', '')
    
    if not full_phone or len(full_phone) < 8:
        return JsonResponse({'success': False, 'error': 'Invalid phone number'}, status=400)
    
    if not email:
        return JsonResponse({'success': False, 'error': 'Please enter your email'}, status=400)
    
    is_valid, error = validate_email(email)
    if not is_valid:
        return JsonResponse({'success': False, 'error': error}, status=400)
    
    wa_phone = re.sub(r'\D', '', full_phone)
    
    message = f"""🚗 <b>Car Request</b>

🏎 Car: <a href="{car_url}">{car_name}</a>
📅 Date: {date if date else 'Not specified'}
📱 Phone: <a href="https://wa.me/{wa_phone}">{full_phone}</a>
📧 Email: {email}"""
    
    send_telegram(message)
    
    return JsonResponse({'success': True})
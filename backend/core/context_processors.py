# backend/core/context_processors.py

from .models import CodeSnippet

def code_snippets(request):
    """Добавляет code snippets в контекст всех шаблонов"""
    path = request.path
    
    snippets = CodeSnippet.objects.filter(is_active=True)
    
    return {
        'snippets_head_start': [s for s in snippets if s.location == 'head_start' and s.should_show_on_path(path)],
        'snippets_head_end': [s for s in snippets if s.location == 'head_end' and s.should_show_on_path(path)],
        'snippets_body_start': [s for s in snippets if s.location == 'body_start' and s.should_show_on_path(path)],
        'snippets_body_end': [s for s in snippets if s.location == 'body_end' and s.should_show_on_path(path)],
    }


def site_settings(request):
    """Глобальные настройки сайта"""
    return {
        'SITE_NAME': 'Prestige Cars 24',
        'SITE_PHONE': '+39 339 106 9936',
        'SITE_PHONE_CLEAN': '+393391069936',
        'SITE_EMAIL': 'booking@prestigecars24.com',
        'SITE_ADDRESS': 'Via Giacomo Leopardi, 26',
        'SITE_CITY': '20123 Milano MI, Italy',
        'SITE_WHATSAPP': 'https://wa.me/393391069936',
        'SITE_INSTAGRAM': 'https://www.instagram.com/prestigecars24/',
        'SITE_TIKTOK': 'https://www.tiktok.com/@prestigecars24/',
        'SITE_FACEBOOK': 'https://www.facebook.com/prestigecars24/',
    }

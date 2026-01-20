from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Count
from django.db.models import Prefetch

from django.views.decorators.http import require_POST


def index(request):
    """Главная страница."""
    return render(request, "pages/home03.html")


def privacy_policy(request):
    return render(request, 'pages/privacy_policy.html')


def terms_of_use(request):
    return render(request, 'pages/terms_of_use.html')


def developer_award_2025(request):
    return render(request, 'pages/developer_award_2025.html')

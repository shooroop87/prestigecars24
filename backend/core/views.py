from django.shortcuts import render


def index(request):
    """Главная страница."""
    return render(request, "pages/home03.html")


def privacy_policy(request):
    return render(request, 'pages/privacy_policy.html')


def terms_of_use(request):
    return render(request, 'pages/terms_of_use.html')


def developer_award_2025(request):
    return render(request, 'pages/developer_award_2025.html')

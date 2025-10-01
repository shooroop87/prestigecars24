# backend/core/urls.py

from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    # Главная страница
    path("", views.home, name="home"),
    
    # О нас
    #path("about/", views.about, name="about"),
    
    # Контакты
    #path("contact/", views.contact, name="contact"),
    
    # Наш автопарк
    #path("fleet/", views.fleet, name="fleet"),
    
    # Детальная страница автомобиля
    #path("fleet/<slug:slug>/", views.vehicle_detail, name="vehicle_detail"),
]
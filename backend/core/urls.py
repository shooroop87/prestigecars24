from django.urls import path
from . import views

urlpatterns = [
    # Страницы
    path("", views.index, name="index"),
    path("contacts/", views.contacts, name="contacts"),
    path("cookies/", views.cookies, name="cookies"),
    path("privacy-policy/", views.privacy, name="privacy"),
    path("faq/", views.faq, name="faq"),
    
    # API для форм
    path("api/booking/", views.booking_request, name="booking_request"),
    path("api/contact/", views.contact_request, name="contact_request"),
    
    # Машины
    path("<slug:category_slug>/<slug:car_slug>/", views.car_detail, name="car_detail"),
    path("<slug:category_slug>/", views.car_list_by_category, name="car_list_by_category"),
]
from django.urls import path, include
from services import views

urlpatterns = [
    path("", views.service_list, name="service_list"),
    path("<slug:service_slug>/", views.service_detail, name="service_detail"),
]
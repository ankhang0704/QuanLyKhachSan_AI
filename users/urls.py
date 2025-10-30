from django.urls import path, include
from users import views

urlpatterns = [
    path("history/", views.history_booking_view, name="history"),
]
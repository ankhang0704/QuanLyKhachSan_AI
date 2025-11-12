from django.urls import path, include
from users import views

urlpatterns = [
    path("my_bookings/", views.history_booking_view, name="my_bookings"),
    path('my_bookings/cancel/<int:booking_id>/', views.booking_cancel_view, name='booking_cancel'),
    path("my_bookings/detail/<int:booking_id>/", views.my_booking_detail_view, name="my_booking_detail"),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
]
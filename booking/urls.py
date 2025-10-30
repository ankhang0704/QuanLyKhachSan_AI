from django.urls import path, include
from booking import views

urlpatterns = [
    path("rooms/", views.room_list_view, name="room_list"),
    path("rooms/<int:room_id>/", views.room_detail_view, name="room_detail"),
]
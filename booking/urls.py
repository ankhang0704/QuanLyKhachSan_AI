from django.urls import path, include
from booking import views

urlpatterns = [
    # Danh sách các loại phòng
    path("rooms/", views.room_list_view, name="room_list"),
    # Chi tiết loại phòng
    path("rooms/<int:room_id>/", views.room_detail_view, name="room_detail"),
    # Trang kết quả tìm phòng trống
    path("search/", views.search_results_view, name="search_results"),
    # Form xác nhận đặt phòng
    path("confirm/<int:room_type_id>/", views.booking_confirm_form_view, name="booking_confirm_form"),
    # Trang thành công sau khi đặt phòng
    path('success/<int:booking_id>/', views.booking_success_view, name='booking_success'),
]
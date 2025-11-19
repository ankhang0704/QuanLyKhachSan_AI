from django import template
from booking.models import Booking, Room
from django.db.models import Sum, Count
from django.utils import timezone # Cần cái này để lấy ngày hôm nay
import json

register = template.Library()

@register.simple_tag
def get_dashboard_stats():
    today = timezone.now().date()

    # 1. THỐNG KÊ TỔNG QUAN
    total_bookings = Booking.objects.count()
    
    revenue_data = Booking.objects.filter(status='checked_out').aggregate(Sum('total_price'))
    total_revenue = revenue_data['total_price__sum'] or 0

    # 2. THỐNG KÊ VẬN HÀNH HÔM NAY (Rất quan trọng cho Lễ tân)
    # Khách sẽ check-in hôm nay
    arrivals_today = Booking.objects.filter(check_in=today, status='booked').count()
    
    # Khách sẽ check-out hôm nay
    departures_today = Booking.objects.filter(check_out=today, status='checked_in').count()

    # 3. DANH SÁCH 5 ĐƠN MỚI NHẤT (Để hiển thị bảng)
    recent_bookings = Booking.objects.select_related('user', 'room').order_by('-id')[:5]

    # 4. DỮ LIỆU BIỂU ĐỒ (Chart.js)
    # Đếm số lượng đơn theo từng trạng thái
    raw_status_counts = list(Booking.objects.values('status').annotate(count=Count('id')))
    status_counts_json = json.dumps(raw_status_counts)
    # Kết quả dạng: [{'status': 'booked', 'count': 5}, {'status': 'canceled', 'count': 2}...]

    return {
        'total_bookings': total_bookings,
        'total_revenue': total_revenue,
        'arrivals_today': arrivals_today,     # Mới
        'departures_today': departures_today, # Mới
        'recent_bookings': recent_bookings,   # Mới
        'status_counts': status_counts_json,       # Mới (cho biểu đồ)
    }
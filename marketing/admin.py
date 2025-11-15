# marketing/admin.py
from django.contrib import admin
from .models import Promotion

@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    # Hiển thị các cột quan trọng
    list_display = ('title', 'discount_text', 'start_date', 'end_date', 'is_active')
    
    # Bộ lọc bên phải: Lọc theo trạng thái kích hoạt và ngày kết thúc
    list_filter = ('is_active', 'end_date')
    
    # Thanh tìm kiếm theo tên
    search_fields = ('title', 'description')
    
    # Sắp xếp mặc định: Cái nào mới nhất lên đầu
    ordering = ('-start_date',)
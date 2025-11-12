from django.contrib import admin ,messages
from .models import RoomType, Room, Booking, RoomImage, Inventory
from import_export.admin import ImportExportModelAdmin
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget

# Register your models here.

# Inline admin for RoomImage to be used in RoomTypeAdmin
class RoomImageInline(admin.TabularInline):
    model = RoomImage # Sử dụng bảng trung gian tự động tạo bởi Django
    extra = 1  # Hiển thị sẵn 1 slot upload ảnh mới
    fields = ['image', 'is_thumbnail'] # Thêm trường hình ảnh và is_thumbnail vào giao diện admin

# Register RoomType with inline RoomImages
@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    inlines = [RoomImageInline]
    list_display = ('name', 'price_per_night', 'capacity')

# Register Room with import-export functionality
class RoomResource(resources.ModelResource):
    room_type = fields.Field(
        column_name='room_type',
        attribute='room_type',
        widget=ForeignKeyWidget(RoomType, 'name')
    )

    class Meta:
        model = Room
        fields = ('id', 'room_number', 'room_type',)

# Resister RoomAdmin with import-export functionality
@admin.register(Room)
class RoomAdmin(ImportExportModelAdmin):
    resource_class = RoomResource
    list_display = ('room_number', 'room_type')
    list_filter = ('room_type',)


# Register Inventory with import-export functionality
class InventoryResource(resources.ModelResource):
    class Meta:
        model = Inventory
        fields = ('id', 'room_type', 'date', 'available_count',)
# Resister InventoryAdmin with import-export functionality InventoryResource
@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    resource_class = InventoryResource
    list_display = ('room_type', 'date', 'available_count')
    list_filter = ('room_type', 'date')
    search_fields = ('room_type__name',)
    ordering = ('room_type', 'date')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    
    # --- CÁC TÙY CHỈNH CŨ (Giữ nguyên) ---
    list_display = (
        'id', 
        'user', 
        'room', 
        'room_type_display',
        'check_in', 
        'check_out', 
        'status', # Cột này rất quan trọng
        'total_price'
    )
    list_filter = ('status', 'check_in', 'room__room_type',)
    search_fields = ('id', 'user__username', 'room__room_number',)
    date_hierarchy = 'check_in'
    
    @admin.display(description='Loại phòng', ordering='room__room_type')
    def room_type_display(self, obj):
        return obj.room.room_type.name

    # --- 2. THÊM CÁC HÀNH ĐỘNG MỚI (Admin Actions) ---
    
    # (Django sẽ tự động thêm các hàm này vào menu "Actions" trong Admin)
    
    @admin.action(description="Đánh dấu các đơn đã CHECK-IN")
    def mark_checked_in(self, request, queryset):
        # 'queryset' là danh sách các đơn (rows) mà Lễ tân đã tick chọn
        
        # Chỉ cập nhật các đơn đang 'booked'
        updated_count = queryset.filter(status='booked').update(status='checked_in')
        
        self.message_user(
            request,
            f"{updated_count} đơn đặt phòng đã được cập nhật sang 'Checked In'.",
            messages.SUCCESS
        )

    @admin.action(description="Đánh dấu các đơn đã CHECK-OUT")
    def mark_checked_out(self, request, queryset):
        # Chỉ cập nhật các đơn đang 'checked_in'
        updated_count = queryset.filter(status='checked_in').update(status='checked_out')
        
        self.message_user(
            request,
            f"{updated_count} đơn đặt phòng đã được cập nhật sang 'Checked Out'.",
            messages.SUCCESS
        )

    # 3. KÍCH HOẠT CÁC NÚT HÀNH ĐỘNG
    actions = [mark_checked_in, mark_checked_out]
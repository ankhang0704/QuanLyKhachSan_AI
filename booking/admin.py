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
    list_display = ('room_number', 'room_type','status')
    list_filter = ('room_type','status',)


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
    
    @admin.action(description="CHECK-IN (Chuyển phòng sang 'Có khách')")
    def mark_checked_in(self, request, queryset):
        # Bước 1: Lọc ra các đơn hợp lệ (đang ở trạng thái 'booked')
        bookings_to_checkin = queryset.filter(status='booked')
        count = 0

        if bookings_to_checkin.exists():
            for booking in bookings_to_checkin:
                # Logic cập nhật Booking
                booking.status = 'checked_in'
                booking.save()
                
                # Logic cập nhật Phòng (Quan trọng)
                if booking.room:
                    booking.room.status = 'occupied' # Chuyển sang "Đang có khách"
                    booking.room.save()
                
                count += 1
            
            self.message_user(
                request, 
                f"Đã check-in thành công cho {count} phòng. Trạng thái phòng đã chuyển sang 'Occupied'.", 
                messages.SUCCESS
            )
        else:
            self.message_user(request, "Không có đơn nào hợp lệ để Check-in (Phải ở trạng thái 'Đã đặt').", messages.WARNING)

    @admin.action(description="CHECK-OUT (Chuyển phòng sang 'Bẩn')")
    def mark_checked_out(self, request, queryset):
        # Bước 1: Lọc ra các đơn hợp lệ (đang ở trạng thái 'checked_in')
        bookings_to_checkout = queryset.filter(status='checked_in')
        count = 0

        if bookings_to_checkout.exists():
            for booking in bookings_to_checkout:
                # Logic cập nhật Booking
                booking.status = 'checked_out'
                booking.save()
                
                # Logic cập nhật Phòng (QUAN TRỌNG NHẤT)
                if booking.room:
                    booking.room.status = 'dirty' # Chuyển sang "Bẩn" để báo dọn dẹp
                    booking.room.save()
                
                count += 1

            self.message_user(
                request, 
                f"Đã check-out {count} đơn. Các phòng liên quan đã được đánh dấu là 'Bẩn' (Cần dọn dẹp).", 
                messages.SUCCESS
            )
        else:
            self.message_user(request, "Không có đơn nào hợp lệ để Check-out (Phải ở trạng thái 'Đang ở').", messages.WARNING)

    # 3. KÍCH HOẠT CÁC NÚT HÀNH ĐỘNG
    actions = [mark_checked_in, mark_checked_out]
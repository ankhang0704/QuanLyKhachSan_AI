# booking/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Booking, Inventory
from datetime import timedelta

# Hàm trợ giúp (helper function)
def update_inventory_range(room_type, start_date, end_date, change_amount):
    # Cập nhật tồn kho cho một khoảng ngày (start_date đến end_date)
    current_date = start_date
    while current_date < end_date: # Chỉ cập nhật đến ngày TRƯỚC ngày check-out
        try:
            inv = Inventory.objects.get(
                room_type=room_type,
                date=current_date
            )
            inv.available_count += change_amount
            inv.save()
        except Inventory.DoesNotExist:
            # (Trường hợp này hiếm khi xảy ra nếu bạn đã populate)
            print(f"Lỗi: Không tìm thấy tồn kho cho {room_type.name} ngày {current_date}")
        current_date += timedelta(days=1)
# Lắng nghe sự kiện 'post_save' (sau khi lưu) của model Booking
@receiver(post_save, sender=Booking)
def handle_new_booking(sender, instance, created, **kwargs):
    # 'created' = True có nghĩa là đây là 1 đơn MỚI
    if created and instance.status == 'booked':
        print(f"Signal: Đơn mới #{instance.id}. Trừ 1 phòng {instance.room.room_type.name}")
        # Trừ 1 phòng khỏi kho
        update_inventory_range(
            instance.room.room_type,
            instance.check_in,
            instance.check_out,
            -1 # Trừ 1
        )
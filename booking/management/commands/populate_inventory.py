# booking/management/commands/populate_inventory.py
from django.core.management.base import BaseCommand
from booking.models import RoomType, Inventory, Room
from datetime import date, timedelta

class Command(BaseCommand):
    help = 'Khởi tạo bảng tồn kho (Inventory) cho 365 ngày tới'

    def handle(self, *args, **options):
        self.stdout.write("Bắt đầu khởi tạo tồn kho...")

        # 1. Lấy ngày hôm nay
        start_date = date.today()

        # 2. Lặp qua 365 ngày tới
        for i in range(365):
            current_date = start_date + timedelta(days=i)

            # 3. Lặp qua TẤT CẢ các loại phòng
            for room_type in RoomType.objects.all():

                # 4. Đếm xem khách sạn có TỔNG CỘNG bao nhiêu phòng loại này
                # (Dựa trên số phòng Cụ thể 'Room' bạn đã import)
                total_rooms_of_type = Room.objects.filter(room_type=room_type).count()

                # 5. Tạo hoặc Lấy bản ghi tồn kho
                # (get_or_create: Tự động kiểm tra, nếu chưa có thì tạo mới)
                inv, created = Inventory.objects.get_or_create(
                    room_type=room_type,
                    date=current_date,
                    # 'defaults' chỉ được dùng khi 'created' (tạo mới)
                    defaults={'available_count': total_rooms_of_type}
                )

                if created:
                    self.stdout.write(f"  > Đã tạo tồn kho cho {room_type.name} ngày {current_date}")
                else:
                    # (Nếu đã tồn tại, có thể cập nhật lại nếu muốn)
                    # inv.available_count = total_rooms_of_type 
                    # inv.save()
                    pass

        self.stdout.write(self.style.SUCCESS("Hoàn thành khởi tạo tồn kho!"))
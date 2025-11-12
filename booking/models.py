from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import date

# Create your models here.
# Mô hình cho phòng còn lại
class Inventory(models.Model):
    room_type = models.ForeignKey('RoomType', on_delete=models.CASCADE)
    date = models.DateField()
    available_count = models.IntegerField(default=0)

    class Meta:
        unique_together = ('room_type', 'date')
        ordering = ['date']

    def __str__(self):
        return f'Inventory for {self.room_type.name} on {self.date}: {self.available_count} rooms available'
# Mô hình cho loại phòng
class RoomType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    capacity = models.IntegerField()

    def __str__(self):
        return self.name

    # Dùng để lấy ảnh đại diện cho loại phòng
    def get_thumbnail_image(self):
        try:
            thumbnail = self.images.get(is_thumbnail=True)
            return thumbnail.image.url
        except RoomImage.DoesNotExist:
            first_image = self.images.first()
            if first_image:
                return first_image.image.url
        return None

# Mô hình cho ảnh phòng
class RoomImage(models.Model):
    room_type = models.ForeignKey(
        RoomType, 
        on_delete=models.CASCADE, 
        related_name='images'
    )
    #File anh
    image = models.ImageField(upload_to='room_types_gallery/')

    # Ảnh đại diện cho loại phòng
    is_thumbnail = models.BooleanField(
        default=False,
        help_text='Đánh dấu nếu đây là ảnh đại diện cho loại phòng này.'
        )

    def __str__(self):
        return f'Ảnh cho {self.room_type.name}'
# Model for Rooms
class Room(models.Model):
    room_number = models.CharField(max_length=10, unique=True)
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE)

    def __str__(self):
        return f'Room {self.room_number} - {self.room_type.name}'

# Mô hình cho đặt phòng
class Booking(models.Model):

    # Trạng thái đặt phòng
    STATUS_BOOKED = 'booked'
    STATUS_CHECKED_IN = 'checked_in'
    STATUS_CHECKED_OUT = 'checked_out'
    STATUS_CANCELED = 'canceled'
    STATUS_CHOICES = [
        (STATUS_BOOKED, 'Xác nhận'), # Đã đổi thành 'Xác nhận' (Confirmed)
        (STATUS_CHECKED_IN, 'Đã nhận phòng'),
        (STATUS_CHECKED_OUT, 'Đã trả phòng'),
        (STATUS_CANCELED, 'Đã hủy'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    check_in = models.DateField()
    check_out = models.DateField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    booked_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_BOOKED)

    # Validate that check-out date is after check-in date
    def clean(self):
        if self.check_in >= self.check_out:
            raise ValidationError('Ngày trả phòng phải sau ngày nhận phòng.')
    
    # Tự động tính total_price khi lưu booking
    def save(self, *args, **kwargs):
            # Tự động tính giá nếu nó chưa được cung cấp
            if not self.total_price and self.room:
                # Tính số đêm
                nights = (self.check_out - self.check_in).days
                if nights <= 0:
                    nights = 1
                
                self.total_price = self.room.room_type.price_per_night * nights
            
            super().save(*args, **kwargs) 
    @property
    def is_cancellable(self):
        """
        Trả về True nếu đơn này được phép hủy.
        Logic: Phải có status 'booked' VÀ ngày check-in phải ở tương lai.
        """
        return (self.status == 'booked') and (self.check_in > date.today())

    def __str__(self):
        return f'Booking by {self.user.username} for {self.room.room_number} from {self.check_in} to {self.check_out}'
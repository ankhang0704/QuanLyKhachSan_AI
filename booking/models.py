from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError

# Create your models here.

# Model for Room Types
class RoomType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    capacity = models.IntegerField()
    image = models.ImageField(upload_to='room_types/')
    
    def __str__(self):
        return self.name

# Model for Rooms
class Room(models.Model):
    room_number = models.CharField(max_length=10, unique=True)
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE)

    def __str__(self):
        return f'Room {self.room_number} - {self.room_type.name}'

# Model for Bookings
class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    check_in = models.DateField()
    check_out = models.DateField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    booked_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=[
        ('booked', 'Booked'),
        ('checked_in', 'Checked In'),
        ('checked_out', 'Checked Out'),
        ('canceled', 'Canceled'),
    ], default='booked')

    # Validate that check-out date is after check-in date
    def clean(self):
        if self.check_in >= self.check_out:
            raise ValidationError('Ngày trả phòng phải sau ngày nhận phòng.')
    
    # Tự động tính total_price khi lưu booking
    def save(self, *args, **kwargs):
        if not self.total_price and self.room:
            nights = (self.check_out - self.check_in).days
            if nights < 0:
                nights = 1
            
            # Lấy giá phòng từ kiểu phòng
            self.total_price == self.room.room_type.price_per_night * nights
        # Gọi phương thức save gốc
        super().save(*args, **kwargs)
 

    def __str__(self):
        return f'Booking by {self.user.username} for {self.room.room_number} from {self.check_in} to {self.check_out}'
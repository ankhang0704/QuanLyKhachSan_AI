from django.db import models
from django.utils import timezone
from booking.models import RoomType


# Model cho các chương trình khuyến mãi
class Promotion(models.Model):
    title = models.CharField(max_length=200, verbose_name="Tên chương trình")
    description = models.TextField(verbose_name="Mô tả")
    discount_text = models.CharField(max_length=100, help_text="VD: Giảm 20%", verbose_name="Mức giảm")
    image = models.ImageField(upload_to='promotions/')
    
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)

    target_room_types = models.ManyToManyField(
        RoomType, 
        blank=True, 
        related_name='promotions',
        verbose_name="Áp dụng cho loại phòng"
    )

    def __str__(self):
        return self.title
    
    # Hàm kiểm tra xem khuyến mãi còn hạn không
    @property
    def is_valid(self):
        today = timezone.now().date()
        return self.is_active and self.start_date <= today <= self.end_date
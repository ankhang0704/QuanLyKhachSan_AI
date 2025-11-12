# services/models.py
from django.db import models
from django.utils.text import slugify

# Định nghĩa các lựa chọn (Choices)
SERVICE_CATEGORY_CHOICES = (
    ('DINING', 'Nhà hàng & Ăn uống'),
    ('WELLNESS', 'Spa & Sức khỏe'),
    ('RECREATION', 'Giải trí & Thể thao'),
    ('OTHER', 'Khác'),
)

# === MODEL 1: DỊCH VỤ CHÍNH ===
class Service(models.Model):
    name = models.CharField(max_length=255) # VD: Ocean Spa, Phòng Gym
    
    category = models.CharField(
        max_length=20, 
        choices=SERVICE_CATEGORY_CHOICES, 
        default='RECREATION'
    )
    
    description = models.TextField(help_text="Mô tả chi tiết về dịch vụ")
    
    # TRƯỜNG MỚI: Giờ mở cửa (dùng CharField cho linh hoạt)
    opening_hours = models.CharField(
        max_length=100, 
        blank=True, 
        help_text="VD: 09:00 - 22:00 (Hàng ngày)"
    )
    
    # TRƯỜNG MỚI: Quy định/Luật lệ
    rules = models.TextField(
        blank=True, 
        help_text="Quy định sử dụng, yêu cầu trang phục, v.v."
    )
    
    # TRƯỜNG PHÍ DỊCH VỤ
    price_info = models.CharField(
        max_length=100, 
        help_text="VD: 'Miễn phí cho khách' hoặc 'Từ 500,000 VNĐ'"
    ) 
    
    slug = models.SlugField(unique=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Tự động tạo slug
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    # Hàm trợ giúp để lấy ảnh đại diện
    def get_main_image(self):
        try:
            # Ưu tiên lấy ảnh được đánh dấu 'is_main'
            main_image = self.gallery.get(is_main=True)
            return main_image.image.url
        except ServiceImage.DoesNotExist:
            # Nếu không có, lấy ảnh đầu tiên
            first_image = self.gallery.first()
            if first_image:
                return first_image.image.url
        return None # Hoặc trả về ảnh placeholder

# === MODEL 2: GALLERY ẢNH CHO DỊCH VỤ ===
class ServiceImage(models.Model):
    # Liên kết với Model Service
    service = models.ForeignKey(
        Service, 
        on_delete=models.CASCADE,
        related_name='gallery' # Dùng 'gallery' để gọi (VD: service.gallery.all)
    )
    
    image = models.ImageField(upload_to='service_gallery/')
    caption = models.CharField(max_length=255, blank=True) # Chú thích ảnh
    
    # Đánh dấu ảnh này là ảnh đại diện
    is_main = models.BooleanField(
       default=False, 
       help_text="Đánh dấu nếu đây là ảnh đại diện chính"
    )

    def __str__(self):
        return f"Ảnh cho {self.service.name}"
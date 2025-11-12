from django.apps import AppConfig


class BookingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'booking'

    def ready(self):
        import booking.signals  # Đảm bảo rằng signals được đăng ký khi ứng dụng sẵn sàng
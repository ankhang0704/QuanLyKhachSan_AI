from django.contrib import admin
from .models import Service, ServiceImage

# Register your models here.


class ServiceImageInline(admin.TabularInline):
    model = ServiceImage
    extra = 1
    fields = ['image', 'caption', 'is_main'] # Các trường để hiển thị

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price_info',)
    list_filter = ('category',) 
    search_fields = ('name', 'description',)
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ServiceImageInline] # <-- Thêm Inline vào đây
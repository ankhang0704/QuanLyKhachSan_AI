from django.contrib import admin
from .models import Post

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    # Hiển thị tiêu đề và ngày tạo
    list_display = ('title', 'created_at')
    
    # Thanh tìm kiếm
    search_fields = ('title', 'content')
    
    # --- QUAN TRỌNG ---
    # Tự động điền field 'slug' khi bạn gõ 'title'
    # Giúp người viết bài không phải tự gõ slug thủ công
    prepopulated_fields = {'slug': ('title',)}
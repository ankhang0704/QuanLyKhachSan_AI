import re
import os
import json
import logging
from django.utils.timezone import datetime
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from booking.models import RoomType
from booking.models import RoomImage
from services.models import ServiceImage

def home_view(request):
    # Truyền 4 loại phòng ngẫu nhiên lên trang chủ
    room_types = RoomType.objects.all().order_by('?')[:4] 
    
    context = {
        'rooms': room_types,
    }   
    return render(request, 'pages/home.html', context)

def about_view(request):
    return render(request, "pages/about.html")

def contact_view(request):
    return render(request, "pages/contact.html")

def gallery_view(request):
    
    # 1. Lấy ảnh phòng (giữ nguyên)
    room_images = RoomImage.objects.all().order_by('-is_thumbnail')
    
    # 2. Lấy TẤT CẢ ảnh dịch vụ
    # Dùng 'select_related' để tối ưu, tránh N+1 query
    all_service_images = ServiceImage.objects.select_related('service').all().order_by('-is_main')
    
    # 3. TẠO TỪ ĐIỂN NHÓM ẢNH (LOGIC MỚI)
    service_galleries = {}
    for img in all_service_images:
        # Lấy tên hiển thị của category (VD: "Spa & Sức khỏe")
        category_name = img.service.get_category_display() 
        
        # Nếu category này chưa có trong từ điển, tạo một list rỗng
        if category_name not in service_galleries:
            service_galleries[category_name] = []
            
        # Thêm ảnh vào đúng nhóm category
        service_galleries[category_name].append(img)
        
    context = {
        'room_images': room_images,
        'service_galleries': service_galleries, # Gửi từ điển đã nhóm
        'all_images': list(room_images) + list(all_service_images)
    }
    return render(request, 'pages/gallery.html', context)
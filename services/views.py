from django.shortcuts import render, get_object_or_404
from .models import Service

# View cho trang services.html (Danh sách)
def service_list(request):
    all_services = Service.objects.all().order_by('category', 'name')
    
    # Khởi tạo từ điển để lưu trữ dịch vụ đã phân loại
    categorized_services = {}
    
    # Lặp qua tất cả dịch vụ và nhóm chúng lại
    for service in all_services:
        # Lấy tên hiển thị của Category (VD: "Spa & Sức khỏe")
        category_name = service.get_category_display() 
        
        # Nếu Category này chưa tồn tại trong từ điển, khởi tạo nó
        if category_name not in categorized_services:
            categorized_services[category_name] = []
            
        # Thêm dịch vụ vào danh sách tương ứng với Category
        categorized_services[category_name].append(service)

    context = {
        # Gửi từ điển các nhóm dịch vụ đến template
        'categorized_services': categorized_services
    }
    return render(request, 'services/services.html', context)

# View cho trang service_detail.html (Chi tiết)
def service_detail(request, service_slug): # Nhận 'slug' từ URL
    # 1. Lấy MỘT dịch vụ (dựa trên slug), nếu không thấy thì báo lỗi 404
    service = get_object_or_404(Service, slug=service_slug)
    
    # 2. Gửi 1 object đó ra template
    context = {
        'service': service
    }
    return render(request, 'services/service_detail.html', context)
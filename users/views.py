from django.shortcuts import render
from booking.models import Booking
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from datetime import date
from django.shortcuts import redirect
from django.contrib import messages
from booking.signals import update_inventory_range
from booking.models import RoomType
from .forms import ProfileEditForm
from django.urls import reverse_lazy
from django.views.generic import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import User
from django.utils import timezone # Thêm import này
from booking.models import Booking # Thêm import này


# Create your views here.
# View để hiển thị lịch sử đặt phòng của user với các bộ lọc nâng cao
@login_required
def history_booking_view(request):
    # 1. Khởi tạo QuerySet cơ bản
    user_bookings = Booking.objects.filter(
        user=request.user
    ).order_by('-booked_at') # Sắp xếp theo ngày đặt (booked_at) thay vì check_in
    
    # 2. Xử lý logic lọc từ request.GET
    room_type_id = request.GET.get('room_type')
    status_filter = request.GET.get('status')
    check_in_date = request.GET.get('check_in_date')

    if room_type_id:
        # Lọc theo loại phòng (Giả định Room Model có ForeignKey tới RoomType)
        user_bookings = user_bookings.filter(room__room_type__id=room_type_id)

    if status_filter:
        # Lọc theo trạng thái
        user_bookings = user_bookings.filter(status=status_filter)

    if check_in_date:
        # Lọc theo ngày nhận phòng
        user_bookings = user_bookings.filter(check_in__gte=check_in_date)
        
    # 3. Chuẩn bị các biến cần thiết cho Frontend
    
    # Lấy danh sách các loại phòng (để điền vào dropdown lọc)
    # Giả định bạn có RoomType model
    room_types_list = RoomType.objects.all() 
    
    # Lấy danh sách các lựa chọn trạng thái từ Model
    status_choices = Booking._meta.get_field('status').choices

    context = {
        'bookings': user_bookings,
        'room_types_list': room_types_list,
        'status_choices': status_choices,
        'current_filters': request.GET, # Truyền các tham số đang lọc để giữ trạng thái trên form
    }
    return render(request, 'users/my_bookings.html', context)

# View chi tiết đơn đặt phòng của user
@login_required #
def my_booking_detail_view(request, booking_id):
    
    # Logic cốt lõi:
    # 1. Lấy đơn đặt phòng theo 'id' (booking_id)
    # 2. VÀ (AND) lọc user=request.user (để bảo mật)
    # Nếu không tìm thấy (do sai ID hoặc không phải của user), nó sẽ báo lỗi 404.
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    context = {
        'booking': booking
    }
    return render(request, 'users/my_booking_detail.html', context)


# View hủy đơn đặt phòng của user
@login_required
def booking_cancel_view(request, booking_id):
    # Bảo mật: Lấy đơn đặt phòng VÀ đảm bảo nó thuộc về user đang đăng nhập
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)  
    # === Xử lý logic nghiệp vụ ===  
    # 1. Kiểm tra xem đơn này có được phép hủy không?
    if not booking.is_cancellable:
        messages.error(request, "Bạn không thể hủy đơn đặt phòng này (có thể đã quá hạn hoặc đã check-in).")
        return redirect('my_booking_detail', booking_id=booking.id)

    # === Xử lý POST (Khi người dùng nhấn nút "Xác nhận hủy") ===
    if request.method == 'POST':
        # Cập nhật trạng thái
        booking.status = 'canceled'
        booking.save()
        
        # --- THÊM LOGIC CỘNG KHO ---
        print(f"View Cancel: Đơn #{booking.id} đã hủy. Cộng 1 phòng {booking.room.room_type.name}")
        update_inventory_range(
            booking.room.room_type,
            booking.check_in,
            booking.check_out,
            +1 # Cộng 1
        )
        messages.success(request, f"Đã hủy thành công đơn đặt phòng #{booking.id}.")
        return redirect('my_bookings')
    context = {
        'booking': booking
    }
    return render(request, 'users/booking_cancel.html', context)

# View về thông tin của người dùng
@login_required
def profile_view(request):
    has_social_account = request.user.socialaccount_set.exists()
    
    # --- THÊM LOGIC TÌM KIẾM NÀY ---
    # Lấy đơn đặt phòng SẮP TỚI (check_in >= hôm nay)
    upcoming_booking = Booking.objects.filter(
        user=request.user,
        status='booked', # Chỉ lấy đơn còn hiệu lực
        check_in__gte=timezone.now().date() # Lớn hơn hoặc bằng hôm nay
    ).order_by('check_in').first() # Lấy đơn gần nhất
    # ---------------------------------
    
    context = {
        'has_social_account': has_social_account,
        'upcoming_booking': upcoming_booking # Gửi đơn này sang template
    }
    return render(request, 'users/profile.html', context)

class ProfileEditView(LoginRequiredMixin, UpdateView):

    model = User 
        # Chỉ định form tùy chỉnh (chỉ có first_name, last_name)
    form_class = ProfileEditForm 
    
    template_name = 'users/profile_edit.html' 
    success_url = reverse_lazy('profile') 

    def get_object(self):
        # Đảm bảo người dùng chỉ sửa chính họ
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Cập nhật hồ sơ thành công!")
        return super().form_valid(form)

# Gán view (để urls.py gọi)
profile_edit_view = ProfileEditView.as_view()


from django.shortcuts import render
from django.shortcuts import get_object_or_404
from datetime import datetime
from booking.models import Booking, Room, RoomType, Inventory
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages
from django.db.models import Min
from django.db import transaction

def room_list_view(request):

    all_room_types = RoomType.objects.all()

    context = {
        "rooms": all_room_types
    }
    return render(request, "booking/room_list.html", context)

def room_detail_view(request, room_id):

    room = get_object_or_404(RoomType, id=room_id)  # Assuming Room is a model defined elsewhere

    context = {
        "room_type": room
    }
    return render(request, "booking/room_detail.html", context)

def search_results_view(request):
    check_in_str = request.GET.get('check_in')
    check_out_str = request.GET.get('check_out')

    if not check_in_str or not check_out_str:
        return render(request, 'booking/search_results.html', {})

    try:
        check_in = datetime.strptime(check_in_str, '%Y-%m-%d').date()
        check_out = datetime.strptime(check_out_str, '%Y-%m-%d').date()
        if check_in >= check_out:
             return render(request, 'booking/search_results.html', {'error': 'Ngày trả phòng phải sau ngày nhận phòng.'})
    except ValueError:
        return render(request, 'booking/search_results.html', {'error': 'Định dạng ngày không hợp lệ.'})
    
    # 1. Tìm các bản ghi Inventory (Tồn kho)
    inventory_in_range = Inventory.objects.filter(
        date__gte=check_in,
        date__lt=check_out # Quan trọng: Chỉ tính các đêm ở, nên < check_out
    )
    
    # 2. Nhóm theo RoomType và tìm Min (ít nhất)
    #    (Nếu 1 ngày còn 0 phòng, thì Min=0)
    #    Kết quả: [{'room_type_id': 1, 'min_available': 5}, 
    #              {'room_type_id': 2, 'min_available': 0}]
    room_type_availability = inventory_in_range.values(
        'room_type_id'
    ).annotate(
        min_available=Min('available_count')
    )
    
    # 3. Lọc ra các ID của loại phòng VẪN CÒN TRỐNG (Min > 0)
    available_room_type_ids = [
        item['room_type_id'] for item in room_type_availability 
        if item['min_available'] > 0
    ]
    
    # 4. Lấy các đối tượng RoomType
    available_room_types = RoomType.objects.filter(id__in=available_room_type_ids)

    # Lưu ngày vào session để dùng cho bước đặt phòng    
    request.session['booking_check_in'] = check_in_str
    request.session['booking_check_out'] = check_out_str
    
    context = {
        'room_types': available_room_types,
        'check_in': check_in,
        'check_out': check_out,
    }
    return render(request, 'booking/search_results.html', context)

@login_required
def booking_success_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    context = {
        'booking': booking
    }
    return render(request, 'booking/booking_success.html', context)

@login_required 
@transaction.atomic
def booking_confirm_form_view(request, room_type_id):
    room_type = get_object_or_404(RoomType, id=room_type_id)
    
    check_in_str = request.session.get('booking_check_in')
    check_out_str = request.session.get('booking_check_out')
    if not check_in_str or not check_out_str:
        messages.error(request, "Vui lòng chọn ngày trước khi đặt phòng.")
        return redirect('search_results') 

    check_in = datetime.strptime(check_in_str, '%Y-%m-%d').date()
    check_out = datetime.strptime(check_out_str, '%Y-%m-%d').date()
    
                # (Tính toán giá cả)
    num_nights = (check_out - check_in).days or 1
    calculated_price = room_type.price_per_night * num_nights 
    if request.method == 'POST':
        
        # === LOGIC KIỂM TRA LẠI (GIỐNG NHƯ CŨ, NHƯNG BỊ KHÓA) ===
        # Chúng ta vẫn phải tìm 1 phòng cụ thể (VD: 201) để gán
        
        # 3. Dùng select_for_update() để KHÓA các đơn Booking đang xung đột
        conflicting_bookings = Booking.objects.select_for_update().filter(
            room__room_type=room_type,
            status='booked', # Đã sửa ở lần trước
            check_in__lt=check_out,
            check_out__gt=check_in
        ).values_list('room_id', flat=True)
        
        available_rooms = Room.objects.filter(
            room_type=room_type
        ).exclude(
            id__in=conflicting_bookings
        )
        
        if available_rooms.exists():
            room_to_book = available_rooms.first() 
            
            
            # Tạo đơn Booking
            new_booking = Booking.objects.create(
                user=request.user,
                room=room_to_book,
                check_in=check_in,
                check_out=check_out,
                status='booked',
                total_price=calculated_price
            )
            # Tín hiệu (signal) ở Bước 3 sẽ tự động được kích hoạt
            # và TRỪ 1 phòng trong Inventory
            
            del request.session['booking_check_in']
            del request.session['booking_check_out']
            
            return redirect('booking_success', booking_id=new_booking.id)
        
        else:
            messages.error(request, "Rất tiếc, loại phòng này vừa có người khác đặt. Vui lòng thử lại.")
            return redirect('search_results')

    # --- GIAI ĐOẠN 2: (Method GET) ---
    # Chỉ hiển thị trang xác nhận
    context = {
        'room_type': room_type,
        'check_in': check_in,
        'check_out': check_out,
        'total_price': calculated_price,
        'num_nights': num_nights,
    }
    return render(request, 'booking/booking_confirm_form.html', context)
from django.shortcuts import render
from .models import RoomType
from django.shortcuts import get_object_or_404

# Create your views here.
def book_view(request):
    return render(request, "booking/booking_page.html")

def room_list_view(request):

    all_room_types = []  # This would typically be a query to the database

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

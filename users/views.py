from django.shortcuts import render

# Create your views here.
def history_booking_view(request):
    return render(request, 'users/history_booking_page.html')
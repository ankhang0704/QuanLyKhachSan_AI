from django.shortcuts import render
from .models import Promotion
from django.utils import timezone

def offers_view(request):
    today = timezone.now().date()
    # Chỉ lấy các khuyến mãi đang hoạt động và còn hạn
    active_promos = Promotion.objects.filter(
        is_active=True,
        start_date__lte=today,
        end_date__gte=today
    )
    return render(request, 'marketing/offers.html', {'promotions': active_promos})
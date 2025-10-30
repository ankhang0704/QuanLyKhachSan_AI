import re
import os
import json
import logging
from django.utils.timezone import datetime
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from operator import attrgetter
from itertools import chain
# Create your views here.
from django.apps import apps # Cần import

@login_required
def activity_history_views(request):

    #Lấy id của user hiện tại
    current_user_id = request.user.id
    #Lấy model từ apps.py
    PredictionHistory = apps.get_model('predictor', 'PredictionHistory')
    UnemploymentHistory = apps.get_model('predictor', 'UnemploymentHistory')
    #  Truy vấn Lịch sử: Lấy tất cả bản ghi của user hiện tại, sắp xếp mới nhất lên trước
    income_history = PredictionHistory.objects.filter(user__id=current_user_id)
    unemployment_history = UnemploymentHistory.objects.filter(user__id=current_user_id)

    # Thêm một thuộc tính 'type' để phân biệt trong template
    combined_history_list = []
    for record in income_history:
        record.type = 'Thu nhập' # Thêm thuộc tính type
        combined_history_list.append(record)
    for record in unemployment_history:
        record.type = 'Thất nghiệp' # Thêm thuộc tính type
        combined_history_list.append(record)
    # Sắp xếp lại toàn bộ lịch sử theo ngày dự đoán, mới nhất lên trước
    sorted_history = sorted(combined_history_list, key=attrgetter('prediction_date'), reverse=True)

    context = {
        'history': sorted_history, # Truyền danh sách đã sắp xếp vào template
        'count': len(sorted_history) # Đếm tổng số bản ghi
    }

    return render(request, 'users/activity_history.html',  context)
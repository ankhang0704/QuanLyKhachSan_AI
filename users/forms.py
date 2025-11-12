# users/forms.py
from django import forms
from .models import User # (Giả sử bạn dùng CustomUser tên là 'User')
# (Nếu bạn dùng User mặc định, import từ: from django.contrib.auth.models import User)

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number', 'profile_picture']
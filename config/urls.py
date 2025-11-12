"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.conf.urls.static import static


admin.site.site_header = "Quản trị Khách sạn The Sailing Bay"
admin.site.site_title = "Admin The Sailing Bay"
admin.site.index_title = "Chào mừng đến với trang quản trị"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('pages.urls')),
    path('booking/', include('booking.urls')),
    path('user/', include('users.urls')),
    path('api/', include('chatbot.urls')),
    path('services/', include('services.urls')),
    path('accounts/', include('allauth.urls')),
]
urlpatterns += staticfiles_urlpatterns()

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
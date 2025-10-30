from django.urls import path, include
from accounts import views

urlpatterns = [
    path("history/", views.activity_history_views, name="history")
]
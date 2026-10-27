from django.urls import path

from .views import AlertsAPIView

urlpatterns = [
    path("", AlertsAPIView.as_view(), name="alerts"),
]

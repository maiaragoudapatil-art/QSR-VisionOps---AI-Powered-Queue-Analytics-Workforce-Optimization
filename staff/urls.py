from django.urls import path

from .views import BranchStaffAPIView

urlpatterns = [
    path("", BranchStaffAPIView.as_view(), name="branch-staff"),
]

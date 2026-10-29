from django.urls import path
from .views import BranchListAPIView, CameraListCreateAPIView, CameraDetailAPIView, CameraStartAPIView, CameraStopAPIView, CameraStatusAPIView
urlpatterns = [
    path("branches/", BranchListAPIView.as_view(), name="branch-list"),
    path("cameras/", CameraListCreateAPIView.as_view(), name="camera-list-create"),
    path("cameras/<int:pk>/", CameraDetailAPIView.as_view(), name="camera-detail"),
    path("cameras/<int:pk>/start/", CameraStartAPIView.as_view(), name="camera-start"),
    path("cameras/<int:pk>/stop/", CameraStopAPIView.as_view(), name="camera-stop"),
    path("cameras/<int:pk>/status/", CameraStatusAPIView.as_view(), name="camera-status"),
]

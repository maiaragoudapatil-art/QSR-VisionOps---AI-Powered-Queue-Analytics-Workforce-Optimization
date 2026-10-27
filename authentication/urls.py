from django.urls import path

from .views import (
    ProfileAPIView,
    RegisterAPIView,
)

urlpatterns = [

    path(
        "profile/",
        ProfileAPIView.as_view(),
        name="profile",
    ),

    path(
        "register/",
        RegisterAPIView.as_view(),
        name="register",
    ),
]
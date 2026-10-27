from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from authentication.views import SettingsAPIView
from feedback.views import CustomerFeedbackAPIView, RewardsAPIView

def home(request):
    return JsonResponse({
        "message": "QSR VisionOps Backend Running"
    })

urlpatterns = [

    path("admin/",
         admin.site.urls),

    path(
        "api/",
        include("analytics.urls")
    ),

    path(
        "api/dashboard/",
        include("dashboard.urls")
    ),
    path(
        "api/alerts/",
        include("alerts.urls")
    ),
    path("", home),
    
    path(
    "api/token/",
    TokenObtainPairView.as_view(),
    name="token_obtain_pair",
),

    path(
        "api/token/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh",
    ),
    
    path(
    "api/auth/",
    include("authentication.urls")
),
path(
    "api/settings/",
    SettingsAPIView.as_view(),
    name="settings",
),
path(
    "api/rewards/",
    RewardsAPIView.as_view(),
    name="rewards",
),
path(
    "api/feedback/",
    CustomerFeedbackAPIView.as_view(),
    name="customer-feedback",
),
    
]

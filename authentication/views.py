from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import (
    IsAuthenticated,
    AllowAny,
)
from rest_framework import status

from django.contrib.auth import get_user_model
from .models import UserSettings

User = get_user_model()


class ProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "id": request.user.id,
            "username": request.user.username,
            "role": request.user.role,
            "branch": (
                request.user.branch.branch_name
                if request.user.branch_id
                else None
            ),
        })


class SettingsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        settings, _ = UserSettings.objects.get_or_create(
            user=request.user,
            defaults={
                "notification_preferences": {
                    "email": False,
                    "in_app": True,
                },
                "dashboard_refresh_interval": 5,
                "theme_settings": {"mode": "light"},
            },
        )
        return Response({
            "notification_preferences": settings.notification_preferences,
            "dashboard_refresh_interval": settings.dashboard_refresh_interval,
            "theme_settings": settings.theme_settings,
        })

    def post(self, request):
        notification_preferences = request.data.get(
            "notification_preferences"
        )
        refresh_interval = request.data.get(
            "dashboard_refresh_interval"
        )
        theme_settings = request.data.get("theme_settings")

        if (
            not isinstance(notification_preferences, dict)
            or set(notification_preferences) != {"email", "in_app"}
            or not all(
                isinstance(value, bool)
                for value in notification_preferences.values()
            )
        ):
            return Response(
                {
                    "error": (
                        "notification_preferences must contain boolean "
                        "email and in_app values"
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if (
            isinstance(refresh_interval, bool)
            or not isinstance(refresh_interval, int)
            or refresh_interval < 1
        ):
            return Response(
                {"error": "dashboard_refresh_interval must be a positive integer"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if (
            not isinstance(theme_settings, dict)
            or set(theme_settings) != {"mode"}
            or theme_settings.get("mode") not in {"light", "dark", "system"}
        ):
            return Response(
                {
                    "error": (
                        "theme_settings must contain a mode of light, dark, "
                        "or system"
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        settings, _ = UserSettings.objects.get_or_create(user=request.user)
        settings.notification_preferences = notification_preferences
        settings.dashboard_refresh_interval = refresh_interval
        settings.theme_settings = theme_settings
        settings.save(update_fields=[
            "notification_preferences",
            "dashboard_refresh_interval",
            "theme_settings",
        ])

        return Response({
            "notification_preferences": settings.notification_preferences,
            "dashboard_refresh_interval": settings.dashboard_refresh_interval,
            "theme_settings": settings.theme_settings,
        })


class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):

        username = request.data.get(
            "username"
        )

        password = request.data.get(
            "password"
        )

        phone_number = request.data.get(
            "phone_number"
        )

        if not username or not password:
            return Response(
                {
                    "error":
                    "Username and password are required"
                },
                status=400,
            )

        if User.objects.filter(
            username=username
        ).exists():
            return Response(
                {
                    "error":
                    "Username already exists"
                },
                status=400,
            )

        user = User.objects.create_user(
            username=username,
            password=password,
            role="customer",
            phone_number=phone_number,
        )

        return Response({
            "message":
            "Customer created successfully",
            "username":
            user.username,
        })
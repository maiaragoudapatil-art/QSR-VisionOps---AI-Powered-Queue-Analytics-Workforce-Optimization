from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("manager", "Manager"),
        ("staff", "Staff"),
        ("customer", "Customer"),
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="staff"
    )

    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True
    )

    branch = models.ForeignKey(
        "branches.Branch",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} - {self.role}"


class UserSettings(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="settings",
    )
    notification_preferences = models.JSONField(
        default=dict,
    )
    dashboard_refresh_interval = models.PositiveIntegerField(default=5)
    theme_settings = models.JSONField(default=dict)

    def __str__(self):
        return f"Settings - {self.user.username}"

from django.db import models
from branches.models import Branch, Camera


class LiveAnalytics(models.Model):

    branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE
    )

    uploaded_video = models.OneToOneField(
        "UploadedVideo",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="analytics_result",
    )

    camera = models.ForeignKey(
        Camera,
        on_delete=models.CASCADE
    )

    customer_count = models.IntegerField(default=0)

    queue_length = models.IntegerField(default=0)

    average_wait_time = models.IntegerField(default=0)

    occupancy = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.branch} - {self.customer_count}"

class Alert(models.Model):

    ALERT_TYPES = (
        ("queue", "Queue Alert"),
        ("wait_time", "Wait Time Alert"),
        ("occupancy", "Occupancy Alert"),
        ("staff_shortage", "Staff Shortage"),
    )

    SEVERITY_CHOICES = (
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("critical", "Critical"),
    )

    alert_type = models.CharField(
        max_length=30,
        choices=ALERT_TYPES
    )

    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_CHOICES,
        default="medium"
    )

    branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE
    )

    camera = models.ForeignKey(
        Camera,
        on_delete=models.CASCADE
    )

    message = models.TextField()

    is_resolved = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.message

class AlertEvidence(models.Model):

    alert = models.ForeignKey(
        Alert,
        on_delete=models.CASCADE,
        related_name="evidence"
    )

    image_path = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    video_path = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Evidence - {self.alert.id}"
    
class UploadedVideo(models.Model):

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    )

    branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE
    )

    video_file = models.FileField(
        upload_to="videos/"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )

    processed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    def __str__(self):
        return (
            f"{self.branch.name} - "
            f"{self.video_file.name}"
        )

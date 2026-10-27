from django.db import models


class Branch(models.Model):
    branch_code = models.CharField(max_length=20, unique=True)
    branch_name = models.CharField(max_length=100)

    city = models.CharField(max_length=100)

    address = models.TextField()

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.branch_name

class Camera(models.Model):

    branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE,
        related_name="cameras"
    )

    camera_name = models.CharField(max_length=100)

    camera_code = models.CharField(max_length=50)

    rtsp_url = models.TextField()

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.camera_name

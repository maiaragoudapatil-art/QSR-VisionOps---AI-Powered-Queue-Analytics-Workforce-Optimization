from uuid import uuid4

from rest_framework import serializers
from .models import Camera

class CameraSerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source="branch.branch_name", read_only=True)
    status = serializers.CharField(source="stream_status", read_only=True)
    camera_code = serializers.CharField(required=False)

    class Meta:
        model = Camera
        fields = ("id", "branch", "branch_name", "camera_name", "camera_code", "location", "rtsp_url",
                  "status",
                  "is_active", "stream_status", "occupancy", "queue_length", "estimated_wait_time", "last_seen", "created_at")
        read_only_fields = ("id", "stream_status", "occupancy", "queue_length", "estimated_wait_time", "last_seen", "created_at")

    def validate(self, attrs):
        if self.instance is None and not attrs.get("rtsp_url"):
            raise serializers.ValidationError({"rtsp_url": "This field is required."})
        return attrs

    def create(self, validated_data):
        validated_data.setdefault("camera_code", f"CAM-{uuid4().hex[:12].upper()}")
        return super().create(validated_data)

    def validate_rtsp_url(self, value):
        if not value.lower().startswith(("rtsp://", "rtsps://")):
            raise serializers.ValidationError("Only RTSP/RTSPS URLs are supported.")
        return value

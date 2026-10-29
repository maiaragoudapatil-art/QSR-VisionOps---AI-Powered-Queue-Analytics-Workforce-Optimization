import logging
import uuid

import cv2
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from analytics.models import Alert, AlertEvidence
from staff.models import Staff

logger = logging.getLogger(__name__)

EVENT_RULES = (
    ("queue", "queue_length", 5, "Queue exceeds 5", "high"),
    ("wait_time", "average_wait_time", 10, "Wait exceeds 10 minutes", "medium"),
    ("occupancy", "occupancy", 80, "Occupancy at least 80%", "high"),
)


def record_threshold_alerts(
    camera,
    metrics,
    frame,
    source_video=None,
    created_types=None,
    resolve_inactive=True,
):
    created_types = created_types if created_types is not None else set()

    def create_alert(alert_type, message, severity):
        alert = Alert.objects.create(
            alert_type=alert_type,
            severity=severity,
            branch=camera.branch,
            camera=camera,
            message=message,
        )
        try:
            encoded, image = cv2.imencode(".jpg", frame)
            if encoded:
                image_path = default_storage.save(
                    f"alert_evidence/camera_{camera.pk}/{uuid.uuid4().hex}.jpg",
                    ContentFile(image.tobytes()),
                )
                AlertEvidence.objects.create(
                    alert=alert,
                    image_path=image_path,
                    video_path=source_video,
                )
        except Exception:
            logger.exception("Unable to save evidence for alert %s", alert.pk)

    for alert_type, metric, threshold, message, severity in EVENT_RULES:
        triggered = (
            metrics[metric] >= threshold
            if metric == "occupancy"
            else metrics[metric] > threshold
        )
        active = None
        if resolve_inactive:
            active = Alert.objects.filter(
                camera=camera,
                alert_type=alert_type,
                is_resolved=False,
            ).first()

        if triggered and alert_type not in created_types and (
            not resolve_inactive or active is None
        ):
            create_alert(alert_type, message, severity)
            created_types.add(alert_type)
        elif not triggered and active is not None:
            active.is_resolved = True
            active.save(update_fields=["is_resolved"])

    required_staff = (
        1 if metrics["queue_length"] <= 5
        else 2 if metrics["queue_length"] <= 10
        else 3
    )
    active_staff = Staff.objects.filter(branch=camera.branch, active=True).count()
    staff_shortage = active_staff < required_staff
    staff_alert = None
    if resolve_inactive:
        staff_alert = Alert.objects.filter(
            camera=camera,
            alert_type="staff_shortage",
            is_resolved=False,
        ).first()
    if staff_shortage and "staff_shortage" not in created_types and (
        not resolve_inactive or staff_alert is None
    ):
        create_alert(
            "staff_shortage",
            f"Staff shortage: {active_staff} active staff; {required_staff} recommended",
            "high",
        )
        created_types.add("staff_shortage")
    elif not staff_shortage and staff_alert is not None:
        staff_alert.is_resolved = True
        staff_alert.save(update_fields=["is_resolved"])

    return created_types

from django.test import TestCase
from rest_framework.test import APIClient

from analytics.models import Alert
from branches.models import Branch, Camera


class AlertsAPIViewTests(TestCase):

    def test_returns_latest_alerts_with_required_fields_and_message(self):
        branch = Branch.objects.create(
            branch_code="ALERT-TEST",
            branch_name="Alert Test Branch",
            city="Test City",
            address="Test Address",
        )
        camera = Camera.objects.create(
            branch=branch,
            camera_name="Alert Test Camera",
            camera_code="ALERT-CAM",
            rtsp_url="rtsp://localhost/test",
        )
        older_alert = Alert.objects.create(
            alert_type="queue",
            severity="medium",
            branch=branch,
            camera=camera,
            message="Older alert",
        )
        latest_alert = Alert.objects.create(
            alert_type="occupancy",
            severity="critical",
            branch=branch,
            camera=camera,
            message="Latest alert",
        )

        response = APIClient().get("/api/alerts/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [alert["id"] for alert in response.data],
            [latest_alert.id, older_alert.id],
        )
        self.assertEqual(
            set(response.data[0]),
            {"id", "alert_type", "severity", "created_at", "message"},
        )
        self.assertEqual(response.data[0]["alert_type"], "occupancy")
        self.assertEqual(response.data[0]["severity"], "critical")
        self.assertEqual(response.data[0]["message"], "Latest alert")

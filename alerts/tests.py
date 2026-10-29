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

        from analytics.models import AlertEvidence
        AlertEvidence.objects.create(alert=latest_alert, image_path="evidence/latest.jpg", video_path="videos/source.mp4")
        response = APIClient().get("/api/alerts/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [alert["id"] for alert in response.data],
            [latest_alert.id, older_alert.id],
        )
        self.assertEqual(
            set(response.data[0]),
            {"id", "alert_type", "severity", "created_at", "message", "evidence_image", "source_video", "branch"},
        )
        self.assertEqual(response.data[0]["alert_type"], "occupancy")
        self.assertEqual(response.data[0]["severity"], "critical")
        self.assertEqual(response.data[0]["message"], "Latest alert")
        self.assertEqual(response.data[0]["branch"], "Alert Test Branch")
        self.assertTrue(response.data[0]["evidence_image"].endswith("/media/evidence/latest.jpg"))
        self.assertEqual(response.data[0]["source_video"], "videos/source.mp4")

    def test_filters_by_branch_and_severity(self):
        branch = Branch.objects.create(branch_code="FILTER", branch_name="Filter Branch", city="City", address="Address")
        camera = Camera.objects.create(branch=branch, camera_name="Filter Camera", camera_code="FILTER-CAM", rtsp_url="rtsp://localhost/test")
        Alert.objects.create(alert_type="queue", severity="high", branch=branch, camera=camera, message="Filtered alert")
        response = APIClient().get("/api/alerts/", {"branch": branch.pk, "severity": "high"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["message"], "Filtered alert")

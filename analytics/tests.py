from django.test import TestCase
from rest_framework.test import APIClient

from analytics.models import LiveAnalytics, UploadedVideo
from branches.models import Branch, Camera


class AnalyticsResultsAPIViewTests(TestCase):

    def test_lists_live_results_with_uploaded_video_details(self):
        branch = Branch.objects.create(
            branch_code="TEST",
            branch_name="Test Branch",
            city="Test City",
            address="Test Address",
        )
        camera = Camera.objects.create(
            branch=branch,
            camera_name="Test Camera",
            camera_code="TEST-CAM",
            rtsp_url="rtsp://localhost/test",
        )
        video = UploadedVideo.objects.create(
            branch=branch,
            video_file="videos/test-video.mp4",
            status="completed",
        )
        result = LiveAnalytics.objects.create(
            uploaded_video=video,
            branch=branch,
            camera=camera,
            customer_count=14,
            queue_length=3,
            average_wait_time=45,
            occupancy=60,
        )

        response = APIClient().get("/api/analytics-results/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [{
            "id": result.id,
            "video_name": "test-video.mp4",
            "branch": "Test Branch",
            "customer_count": 14,
            "queue_length": 3,
            "average_wait_time": 45,
            "occupancy": 60,
            "status": "completed",
            "processed_at": None,
        }])


class CameraAlertEvidenceTests(TestCase):
    def test_stream_analytics_creates_alert_and_snapshot_evidence(self):
        from unittest.mock import Mock, patch
        from analytics.camera_streams import CameraStreamWorker
        from analytics.models import Alert, AlertEvidence
        branch = Branch.objects.create(branch_code="EVENT", branch_name="Event Branch", city="City", address="Address")
        camera = Camera.objects.create(branch=branch, camera_name="Event Camera", camera_code="EVENT-CAM", rtsp_url="rtsp://localhost/test")
        encoded_image = Mock()
        encoded_image.tobytes.return_value = b"jpeg-data"
        metrics = {"queue_length": 8, "average_wait_time": 20, "occupancy": 100, "customer_count": 40}
        with patch("analytics.camera_streams.cv2.imencode", return_value=(True, encoded_image)), \
             patch("analytics.alert_evidence.default_storage.save", return_value="alert_evidence/event.jpg"):
            CameraStreamWorker._update_alerts(camera, metrics, object())
        self.assertEqual(Alert.objects.filter(camera=camera, is_resolved=False).count(), 4)
        self.assertEqual(AlertEvidence.objects.count(), 4)
        CameraStreamWorker._update_alerts(camera, metrics, object())
        self.assertEqual(Alert.objects.filter(camera=camera).count(), 4)

    def test_uploaded_video_alert_records_snapshot_and_source_video(self):
        from unittest.mock import Mock, patch
        from analytics.alert_evidence import record_threshold_alerts
        from analytics.models import AlertEvidence
        branch = Branch.objects.create(branch_code="UPLOAD", branch_name="Upload Branch", city="City", address="Address")
        camera = Camera.objects.create(branch=branch, camera_name="Upload Camera", camera_code="UPLOAD-CAM", rtsp_url="rtsp://localhost/test")
        encoded_image = Mock()
        encoded_image.tobytes.return_value = b"jpeg-data"
        with patch("analytics.alert_evidence.cv2.imencode", return_value=(True, encoded_image)), \
             patch("analytics.alert_evidence.default_storage.save", return_value="alert_evidence/upload.jpg"):
            record_threshold_alerts(
                camera,
                {"queue_length": 8, "average_wait_time": 20, "occupancy": 100},
                object(),
                source_video="videos/source.mp4",
                created_types=set(),
                resolve_inactive=False,
            )
        self.assertEqual(AlertEvidence.objects.count(), 4)
        self.assertEqual(AlertEvidence.objects.first().video_path, "videos/source.mp4")

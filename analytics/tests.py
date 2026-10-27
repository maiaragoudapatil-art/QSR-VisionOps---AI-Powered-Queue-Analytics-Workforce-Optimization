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

from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from rest_framework.test import APIClient

from analytics.models import LiveAnalytics
from branches.models import Branch, Camera


class CustomerDashboardAPIViewTests(TestCase):
    def test_branch_query_returns_branch_scoped_metrics(self):
        branch = Branch.objects.create(
            branch_code="CUSTOMER",
            branch_name="Customer Branch",
            city="Test City",
            address="Test Address",
        )
        camera = Camera.objects.create(
            branch=branch,
            camera_name="Customer Camera",
            camera_code="CUSTOMER-CAM",
            rtsp_url="rtsp://localhost/test",
        )
        LiveAnalytics.objects.create(
            branch=branch,
            camera=camera,
            occupancy=65,
            queue_length=4,
            average_wait_time=12,
        )

        response = APIClient().get("/api/dashboard/", {"branch": branch.pk})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["branch_id"], branch.pk)
        self.assertEqual(response.data["branch"], branch.branch_name)
        self.assertEqual(response.data["occupancy"], 65)
        self.assertEqual(response.data["queue_length"], 4)
        self.assertEqual(response.data["average_wait_time"], 12)

    def test_branch_without_analytics_keeps_branch_identity(self):
        branch = Branch.objects.create(
            branch_code="EMPTY",
            branch_name="Empty Branch",
            city="Test City",
            address="Test Address",
        )

        response = APIClient().get("/api/dashboard/", {"branch": branch.pk})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["branch_id"], branch.pk)
        self.assertEqual(response.data["branch"], branch.branch_name)
        self.assertEqual(response.data["message"], "No analytics data available")

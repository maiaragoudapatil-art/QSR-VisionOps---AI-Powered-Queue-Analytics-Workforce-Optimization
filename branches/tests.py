from django.test import TestCase
from rest_framework.test import APIClient
from authentication.models import User
from branches.models import Branch, Camera
from unittest.mock import patch

class CameraAPITests(TestCase):
    def setUp(self):
        self.branch = Branch.objects.create(branch_code="C-TEST", branch_name="Test Branch", city="City", address="Address")
        self.admin = User.objects.create_user(username="cam-admin", password="test-pass", role="admin")
        self.staff = User.objects.create_user(username="cam-staff", password="test-pass", role="staff")
        self.client = APIClient()

    def test_requires_admin_or_manager_role(self):
        self.assertIn(self.client.get("/api/cameras/").status_code, (401, 403))
        self.client.force_authenticate(self.staff)
        self.assertEqual(self.client.get("/api/cameras/").status_code, 403)

    def test_camera_crud_and_status_contract(self):
        self.client.force_authenticate(self.admin)
        branches_response = self.client.get("/api/branches/")
        self.assertEqual(branches_response.data, [{"id": self.branch.pk, "branch_name": "Test Branch"}])
        response = self.client.post("/api/cameras/", {
            "branch": self.branch.pk, "camera_name": "Front", "camera_code": "FRONT",
            "location": "Front entrance", "rtsp_url": "rtsp://localhost/stream",
        }, format="json")
        self.assertEqual(response.status_code, 201)
        camera_id = response.data["id"]
        self.assertEqual(response.data["rtsp_url"], "rtsp://localhost/stream")
        self.assertEqual(response.data["location"], "Front entrance")
        self.assertEqual(response.data["status"], "stopped")
        self.assertTrue(response.data["camera_code"])
        status_response = self.client.get(f"/api/cameras/{camera_id}/status/")
        self.assertEqual(set(status_response.data), {"status", "occupancy", "queue_length", "estimated_wait_time", "last_seen", "active_alerts"})
        self.assertEqual(status_response.data["status"], "stopped")
        response = self.client.patch(f"/api/cameras/{camera_id}/", {"camera_name": "Front door"}, format="json")
        self.assertEqual(response.data["camera_name"], "Front door")
        with patch("branches.views.camera_streams.start"):
            self.assertEqual(self.client.post(f"/api/cameras/{camera_id}/start/").status_code, 202)
        self.assertEqual(self.client.delete(f"/api/cameras/{camera_id}/").status_code, 204)

    def test_authenticated_customer_can_load_branch_choices(self):
        customer = User.objects.create_user(username="branch-customer", password="test-pass", role="customer")
        self.client.force_authenticate(customer)

        response = self.client.get("/api/branches/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [{"id": self.branch.pk, "branch_name": "Test Branch"}])

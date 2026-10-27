from django.test import TestCase
from rest_framework.test import APIClient

from authentication.models import User
from feedback.models import CustomerFeedback


class CustomerRewardsAPIViewTests(TestCase):

    def test_returns_mock_rewards_for_authenticated_customer(self):
        user = User.objects.create_user(
            username="rewards-customer",
            password="test-password",
            role="customer",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get("/api/rewards/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["points"], 250)
        self.assertEqual(response.data["tier"], "Silver")
        self.assertGreater(len(response.data["available_rewards"]), 0)


class CustomerFeedbackAPIViewTests(TestCase):

    def setUp(self):
        self.customer = User.objects.create_user(
            username="feedback-customer",
            password="test-password",
            role="customer",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.customer)

    def test_customer_can_submit_feedback(self):
        response = self.client.post(
            "/api/feedback/",
            {"rating": 5, "comment": "Great service."},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["message"], "Feedback submitted successfully.")
        saved_feedback = CustomerFeedback.objects.get(customer=self.customer)
        self.assertEqual(saved_feedback.rating, 5)
        self.assertEqual(saved_feedback.comments, "Great service.")

    def test_feedback_requires_valid_rating_and_comment(self):
        response = self.client.post(
            "/api/feedback/",
            {"rating": 6, "comment": ""},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(CustomerFeedback.objects.count(), 0)

    def test_non_customer_cannot_submit_feedback(self):
        manager = User.objects.create_user(
            username="feedback-manager",
            password="test-password",
            role="manager",
        )
        self.client.force_authenticate(user=manager)

        response = self.client.post(
            "/api/feedback/",
            {"rating": 4, "comment": "Good."},
            format="json",
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(CustomerFeedback.objects.count(), 0)

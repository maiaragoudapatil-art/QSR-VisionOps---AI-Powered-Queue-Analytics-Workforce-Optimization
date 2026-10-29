from django.test import TestCase
from rest_framework.test import APIClient

from branches.models import Branch
from authentication.models import User, UserSettings


class ProfileAPIViewTests(TestCase):

    def test_profile_includes_user_id_username_role_and_branch(self):
        branch = Branch.objects.create(
            branch_code="PROFILE",
            branch_name="Profile Branch",
            city="Test City",
            address="Test Address",
        )
        user = User.objects.create_user(
            username="profile-user",
            password="test-password",
            role="staff",
            branch=branch,
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get("/api/auth/profile/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {
            "id": user.id,
            "username": "profile-user",
            "role": "staff",
            "branch": "Profile Branch",
        })

    def test_profile_returns_null_for_unassigned_branch(self):
        user = User.objects.create_user(
            username="unassigned-user",
            password="test-password",
            role="customer",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get("/api/auth/profile/")

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.data["branch"])


class RegisterAPIViewRoleTests(TestCase):
    def test_registration_defaults_to_customer(self):
        response = APIClient().post(
            "/api/auth/register/",
            {"username": "new-customer", "password": "test-password"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.get(username="new-customer").role, "customer")
        self.assertEqual(response.data["role"], "customer")

    def test_admin_can_create_selected_existing_roles(self):
        admin = User.objects.create_user(
            username="role-admin",
            password="test-password",
            role="admin",
        )
        client = APIClient()
        client.force_authenticate(admin)

        for role in ("admin", "manager", "staff", "customer"):
            response = client.post(
                "/api/auth/register/",
                {
                    "username": f"created-{role}",
                    "password": "test-password",
                    "role": role,
                },
                format="json",
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(User.objects.get(username=f"created-{role}").role, role)
            self.assertEqual(response.data["role"], role)

    def test_non_admin_cannot_create_elevated_role(self):
        client = APIClient()
        response = client.post(
            "/api/auth/register/",
            {"username": "public-manager", "password": "test-password", "role": "manager"},
            format="json",
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(User.objects.filter(username="public-manager").exists())

    def test_registration_rejects_unknown_role(self):
        admin = User.objects.create_user(
            username="invalid-role-admin",
            password="test-password",
            role="admin",
        )
        client = APIClient()
        client.force_authenticate(admin)

        response = client.post(
            "/api/auth/register/",
            {"username": "unknown-role", "password": "test-password", "role": "unknown"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["error"], "Invalid role")


class SettingsAPIViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="settings-user",
            password="test-password",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_get_returns_defaults_for_new_user(self):
        response = self.client.get("/api/settings/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {
            "notification_preferences": {
                "email": False,
                "in_app": True,
            },
            "dashboard_refresh_interval": 5,
            "theme_settings": {"mode": "light"},
        })

    def test_post_persists_settings_for_authenticated_user(self):
        payload = {
            "notification_preferences": {
                "email": True,
                "in_app": False,
            },
            "dashboard_refresh_interval": 20,
            "theme_settings": {"mode": "dark"},
        }

        response = self.client.post(
            "/api/settings/",
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, payload)

        settings = UserSettings.objects.get(user=self.user)
        self.assertEqual(settings.notification_preferences, payload["notification_preferences"])
        self.assertEqual(settings.dashboard_refresh_interval, 20)
        self.assertEqual(settings.theme_settings, payload["theme_settings"])

    def test_post_rejects_non_positive_refresh_interval(self):
        response = self.client.post(
            "/api/settings/",
            {
                "notification_preferences": {
                    "email": True,
                    "in_app": True,
                },
                "dashboard_refresh_interval": 0,
                "theme_settings": {"mode": "light"},
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)

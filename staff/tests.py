from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from rest_framework.test import APIClient

from authentication.models import User
from branches.models import Branch
from staff.models import Staff


class BranchStaffAPIViewTests(TestCase):
    def test_lists_active_staff_for_requested_branch(self):
        customer = User.objects.create_user(
            username="staff-list-customer",
            password="test-password",
            role="customer",
        )
        branch = Branch.objects.create(
            branch_code="STAFF-LIST",
            branch_name="Staff List Branch",
            city="Test City",
            address="Test Address",
        )
        staff_member = Staff.objects.create(
            employee_id="STAFF-LIST-1",
            name="Active Staff",
            branch=branch,
            shift="Morning",
        )
        Staff.objects.create(
            employee_id="STAFF-LIST-2",
            name="Inactive Staff",
            branch=branch,
            shift="Evening",
            active=False,
        )
        client = APIClient()
        client.force_authenticate(user=customer)

        response = client.get("/api/staff/", {"branch": branch.pk})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [{"id": staff_member.pk, "name": "Active Staff"}])

    def test_requires_branch_parameter(self):
        customer = User.objects.create_user(
            username="staff-list-no-branch",
            password="test-password",
            role="customer",
        )
        client = APIClient()
        client.force_authenticate(user=customer)

        response = client.get("/api/staff/")

        self.assertEqual(response.status_code, 400)


class UserManagementAPIViewTests(TestCase):
    def setUp(self):
        self.branch = Branch.objects.create(
            branch_code="USER-MGMT",
            branch_name="User Management Branch",
            city="Test City",
            address="Test Address",
        )
        self.admin = User.objects.create_user(
            username="user-management-admin",
            password="test-password",
            role="admin",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)

    def test_creates_branch_assigned_staff_and_lists_user(self):
        response = self.client.post(
            "/api/users/",
            {
                "username": "branch-staff",
                "email": "staff@example.com",
                "password": "test-password",
                "role": "staff",
                "branch": self.branch.pk,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        user = User.objects.get(username="branch-staff")
        self.assertEqual(user.role, "staff")
        self.assertEqual(user.branch, self.branch)
        self.assertTrue(Staff.objects.filter(branch=self.branch, name=user.username).exists())
        self.assertEqual(
            self.client.get("/api/users/").data[-1],
            {
                "id": user.pk,
                "username": user.username,
                "email": user.email,
                "role": "staff",
                "branch": self.branch.branch_name,
                "branch_id": self.branch.pk,
            },
        )
        self.assertEqual(
            self.client.get("/api/staff/", {"branch": self.branch.pk}).data,
            [{"id": Staff.objects.get(name=user.username).pk, "name": user.username}],
        )

    def test_creates_manager_with_branch_and_profile_returns_assignment(self):
        response = self.client.post(
            "/api/users/",
            {
                "username": "branch-manager",
                "email": "manager@example.com",
                "password": "test-password",
                "role": "manager",
                "branch": self.branch.pk,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        manager = User.objects.get(username="branch-manager")
        self.assertEqual(manager.role, "manager")
        self.assertEqual(manager.branch, self.branch)

        profile_client = APIClient()
        profile_client.force_authenticate(user=manager)
        profile = profile_client.get("/api/auth/profile/")
        self.assertEqual(profile.data["role"], "manager")
        self.assertEqual(profile.data["branch"], self.branch.branch_name)

    def test_manager_and_staff_require_a_branch(self):
        for role in ("manager", "staff"):
            response = self.client.post(
                "/api/users/",
                {
                    "username": f"no-branch-{role}",
                    "password": "test-password",
                    "role": role,
                },
                format="json",
            )
            self.assertEqual(response.status_code, 400)
            self.assertFalse(User.objects.filter(username=f"no-branch-{role}").exists())

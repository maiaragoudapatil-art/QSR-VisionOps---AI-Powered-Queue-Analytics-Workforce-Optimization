from uuid import uuid4

from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from branches.models import Branch
from feedback.models import Feedback
from .models import Staff

User = get_user_model()


class UserManagementAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def _is_admin(self, request):
        return request.user.role == "admin"

    def get(self, request):
        if not self._is_admin(request):
            return Response(
                {"error": "Only admins can view users."},
                status=status.HTTP_403_FORBIDDEN,
            )

        users = User.objects.select_related("branch").order_by("id")
        return Response([
            {
                "id": user.pk,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "branch": user.branch.branch_name if user.branch_id else None,
                "branch_id": user.branch_id,
            }
            for user in users
        ])

    def post(self, request):
        if not self._is_admin(request):
            return Response(
                {"error": "Only admins can create users."},
                status=status.HTTP_403_FORBIDDEN,
            )

        username = request.data.get("username")
        email = request.data.get("email", "")
        password = request.data.get("password")
        role = request.data.get("role")
        branch_id = request.data.get("branch")

        if not username or not password or not role:
            return Response(
                {"error": "Username, password, and role are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not isinstance(role, str) or role not in {
            choice[0] for choice in User.ROLE_CHOICES
        }:
            return Response(
                {"error": "Invalid role."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if User.objects.filter(username=username).exists():
            return Response(
                {"error": "Username already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if role in {"manager", "staff"} and not branch_id:
            return Response(
                {"error": "A branch is required for managers and staff."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        branch = None
        if branch_id:
            try:
                branch = Branch.objects.get(pk=branch_id, is_active=True)
            except (Branch.DoesNotExist, ValueError, TypeError):
                return Response(
                    {"error": "Select a valid active branch."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        with transaction.atomic():
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                role=role,
                branch=branch,
            )
            if role == "staff":
                Staff.objects.create(
                    employee_id=f"USR-{user.pk}-{uuid4().hex[:8].upper()}",
                    name=username,
                    branch=branch,
                    shift="Unassigned",
                )

        return Response(
            {
                "id": user.pk,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "branch": branch.branch_name if branch else None,
                "branch_id": user.branch_id,
            },
            status=status.HTTP_201_CREATED,
        )


class BranchStaffAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        branch_id = request.query_params.get("branch")
        if not branch_id:
            return Response(
                {"error": "branch is required."},
                status=400,
            )
        try:
            branch_id = int(branch_id)
        except (ValueError, TypeError):
            return Response({"error": "Invalid branch."}, status=400)
        try:
            staff = Staff.objects.filter(
                branch_id=branch_id,
                branch__is_active=True,
                active=True,
            ).order_by("name")
            return Response([
                {"id": member.pk, "name": member.name}
                for member in staff
            ])
        except (ValueError, TypeError):
            return Response({"error": "Invalid branch."}, status=400)


class BestStaffAPIView(APIView):

    def get(self, request):

        best = (
            Feedback.objects
            .order_by("-rating")
            .first()
        )

        if not best:
            return Response({
                "message": "No feedback available"
            })

        return Response({
            "staff": best.staff.name,
            "rating": best.rating,
            "comment": best.comments
        })
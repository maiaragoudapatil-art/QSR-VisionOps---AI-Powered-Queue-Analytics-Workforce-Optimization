from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from branches.models import Branch
from staff.models import Staff
from .models import CustomerFeedback


class RewardsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        points = 250
        rewards = [
            {
                "id": "free-drink",
                "name": "Free Drink",
                "points_required": 100,
                "description": "Redeem for a free drink with your next order.",
            },
            {
                "id": "side-dish",
                "name": "Free Side Dish",
                "points_required": 200,
                "description": "Redeem for a side dish with your next order.",
            },
            {
                "id": "meal-discount",
                "name": "Meal Discount",
                "points_required": 500,
                "description": "Get a discount on a meal.",
            },
        ]

        return Response({
            "points": points,
            "tier": "Silver",
            "available_rewards": [
                reward
                for reward in rewards
                if reward["points_required"] <= points
            ],
        })


class CustomerFeedbackAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role != "customer":
            return Response(
                {"error": "Only customers can submit feedback."},
                status=status.HTTP_403_FORBIDDEN,
            )

        rating = request.data.get("rating")
        comment = request.data.get("comment")
        staff_id = request.data.get("staff_id")
        branch_id = request.data.get("branch")

        if (
            isinstance(rating, bool)
            or not isinstance(rating, int)
            or rating < 1
            or rating > 5
        ):
            return Response(
                {"error": "Rating must be an integer from 1 to 5."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not isinstance(comment, str) or not comment.strip():
            return Response(
                {"error": "Comment is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        staff = None
        branch = None
        if staff_id is not None or branch_id is not None:
            if staff_id is None or branch_id is None:
                return Response(
                    {"error": "Both staff_id and branch are required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                branch = Branch.objects.get(pk=branch_id, is_active=True)
                staff = Staff.objects.get(
                    pk=staff_id,
                    branch=branch,
                    active=True,
                )
            except (Branch.DoesNotExist, Staff.DoesNotExist, ValueError, TypeError):
                return Response(
                    {"error": "Selected staff member is not available for this branch."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        feedback = CustomerFeedback.objects.create(
            customer=request.user,
            rating=rating,
            comments=comment.strip(),
            staff=staff,
            branch=branch,
        )

        return Response(
            {
                "id": feedback.id,
                "staff_id": feedback.staff_id,
                "branch": feedback.branch_id,
                "rating": feedback.rating,
                "comment": feedback.comments,
                "created_at": feedback.created_at,
                "message": "Feedback submitted successfully.",
            },
            status=status.HTTP_201_CREATED,
        )

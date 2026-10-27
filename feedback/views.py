from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

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

        feedback = CustomerFeedback.objects.create(
            customer=request.user,
            rating=rating,
            comments=comment.strip(),
        )

        return Response(
            {
                "id": feedback.id,
                "rating": feedback.rating,
                "comment": feedback.comments,
                "message": "Feedback submitted successfully.",
            },
            status=status.HTTP_201_CREATED,
        )

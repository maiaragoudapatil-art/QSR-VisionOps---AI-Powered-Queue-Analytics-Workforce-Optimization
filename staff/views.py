from rest_framework.views import APIView
from rest_framework.response import Response

from feedback.models import Feedback


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
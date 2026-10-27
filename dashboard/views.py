from rest_framework.views import APIView
from rest_framework.response import Response

from analytics.models import LiveAnalytics


class DashboardAPIView(APIView):

    def get(self, request):

        latest = LiveAnalytics.objects.order_by(
            "-created_at"
        ).first()

        if not latest:
            return Response({
                "message": "No analytics data available"
            })

        queue_length = latest.queue_length

        if queue_length <= 5:
            status = "Normal"
            recommended_staff = 1

        elif queue_length <= 10:
            status = "Warning"
            recommended_staff = 2

        else:
            status = "Critical"
            recommended_staff = 3

        return Response({

            "branch": latest.branch.branch_name,

            "camera": latest.camera.camera_name,

            "customer_count": latest.customer_count,

            "queue_length": latest.queue_length,

            "average_wait_time":
                latest.average_wait_time,

            "occupancy":
                latest.occupancy,

            "status":
                status,

            "recommended_staff":
                recommended_staff

        })
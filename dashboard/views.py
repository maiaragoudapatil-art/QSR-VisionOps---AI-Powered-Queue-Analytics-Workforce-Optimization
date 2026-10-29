from rest_framework.views import APIView
from rest_framework.response import Response

from analytics.models import LiveAnalytics
from branches.models import Branch


class DashboardAPIView(APIView):

    def get(self, request):

        analytics = LiveAnalytics.objects.values(
            "branch_id",
            "branch__branch_name",
            "camera__camera_name",
            "customer_count",
            "queue_length",
            "average_wait_time",
            "occupancy",
            "created_at",
        )
        requested_branch = request.query_params.get("branch")
        if requested_branch:
            try:
                branch = Branch.objects.get(pk=requested_branch, is_active=True)
            except (Branch.DoesNotExist, ValueError):
                return Response({
                    "branch_id": None,
                    "branch": None,
                    "message": "Branch not found",
                })
            analytics = analytics.filter(branch=branch)
        else:
            branch = None

        latest = analytics.order_by(
            "-created_at"
        ).first()

        if not latest:
            response = {"message": "No analytics data available"}
            if branch:
                response.update({
                    "branch_id": branch.pk,
                    "branch": branch.branch_name,
                })
            return Response(response)

        queue_length = latest["queue_length"]

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

            "branch_id": latest["branch_id"],
            "branch": latest["branch__branch_name"],

            "camera": latest["camera__camera_name"],

            "customer_count": latest["customer_count"],

            "queue_length": latest["queue_length"],

            "average_wait_time": latest["average_wait_time"],

            "occupancy": latest["occupancy"],

            "status":
                status,

            "recommended_staff":
                recommended_staff

        })
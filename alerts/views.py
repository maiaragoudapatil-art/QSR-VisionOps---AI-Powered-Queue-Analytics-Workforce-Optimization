from rest_framework.response import Response
from rest_framework.views import APIView

from analytics.models import Alert


class AlertsAPIView(APIView):

    def get(self, request):
        alerts = Alert.objects.order_by("-created_at")
        data = [
            {
                "id": alert.id,
                "alert_type": alert.alert_type,
                "severity": alert.severity,
                "created_at": alert.created_at,
                "message": alert.message,
            }
            for alert in alerts
        ]
        return Response(data)

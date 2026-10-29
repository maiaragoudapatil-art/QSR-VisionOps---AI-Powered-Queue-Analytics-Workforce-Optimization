from django.conf import settings
from django.utils.dateparse import parse_date, parse_datetime
from rest_framework.response import Response
from rest_framework.views import APIView
from analytics.models import Alert

class AlertsAPIView(APIView):
    def get(self, request):
        alerts = Alert.objects.select_related("branch").prefetch_related("evidence").order_by("-created_at")
        branch = request.query_params.get("branch")
        severity = request.query_params.get("severity")
        if branch:
            alerts = alerts.filter(branch_id=branch) if branch.isdigit() else alerts.filter(branch__branch_name=branch)
        if severity:
            alerts = alerts.filter(severity=severity)
        start = request.query_params.get("start_date")
        end = request.query_params.get("end_date")
        if start:
            parsed = parse_datetime(start) or parse_date(start)
            if parsed is None:
                return Response({"error": "Invalid start_date"}, status=400)
            alerts = alerts.filter(created_at__gte=parsed)
        if end:
            parsed = parse_datetime(end) or parse_date(end)
            if parsed is None:
                return Response({"error": "Invalid end_date"}, status=400)
            alerts = alerts.filter(created_at__date__lte=parsed.date() if hasattr(parsed, "date") else parsed)
        data = []
        for alert in alerts:
            evidence = alert.evidence.order_by("-created_at").first()
            image = evidence.image_path if evidence else None
            if image and not image.startswith(("http://", "https://")):
                image = request.build_absolute_uri(image if image.startswith("/") else settings.MEDIA_URL + image)
            data.append({
                "id": alert.id,
                "alert_type": alert.alert_type,
                "severity": alert.severity,
                "created_at": alert.created_at,
                "message": alert.message,
                "evidence_image": image,
                "source_video": evidence.video_path if evidence else None,
                "branch": alert.branch.branch_name,
            })
        return Response(data)

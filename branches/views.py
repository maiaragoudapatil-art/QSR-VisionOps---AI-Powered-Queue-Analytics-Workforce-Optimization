from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from analytics.camera_streams import camera_streams
from analytics.models import Alert
from .models import Branch, Camera
from .permissions import IsCameraAdminOrManager
from .serializers import CameraSerializer

class BranchListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        branches = Branch.objects.filter(is_active=True).order_by("branch_name")
        return Response([
            {"id": branch.pk, "branch_name": branch.branch_name}
            for branch in branches
        ])

class CameraListCreateAPIView(APIView):
    permission_classes = [IsCameraAdminOrManager]
    def get(self, request):
        rows = Camera.objects.select_related("branch").all()
        return Response(CameraSerializer(rows, many=True).data)
    def post(self, request):
        serializer = CameraSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        camera = serializer.save()
        return Response(CameraSerializer(camera).data, status=status.HTTP_201_CREATED)

class CameraDetailAPIView(APIView):
    permission_classes = [IsCameraAdminOrManager]
    def get_object(self, pk):
        return get_object_or_404(Camera.objects.select_related("branch"), pk=pk)
    def patch(self, request, pk):
        return self._update(request, pk, partial=True)
    def put(self, request, pk):
        return self._update(request, pk, partial=False)
    def _update(self, request, pk, partial):
        camera = self.get_object(pk)
        restart = camera.stream_status == "running" and "rtsp_url" in request.data
        if restart and not camera_streams.stop(camera.pk):
            return Response({"error": "Camera stream is still shutting down"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        serializer = CameraSerializer(camera, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        camera = serializer.save()
        if restart:
            camera_streams.start(camera.pk)
        return Response(CameraSerializer(camera).data)
    def delete(self, request, pk):
        camera = self.get_object(pk)
        if not camera_streams.stop(camera.pk):
            return Response({"error": "Camera stream is still shutting down"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        camera.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class CameraStartAPIView(APIView):
    permission_classes = [IsCameraAdminOrManager]
    def post(self, request, pk):
        camera = get_object_or_404(Camera, pk=pk)
        if not camera.is_active:
            return Response({"error": "Camera is inactive"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            camera_streams.start(camera.pk)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_409_CONFLICT)
        return Response({"status": "running"}, status=status.HTTP_202_ACCEPTED)

class CameraStopAPIView(APIView):
    permission_classes = [IsCameraAdminOrManager]
    def post(self, request, pk):
        camera = get_object_or_404(Camera, pk=pk)
        stopped = camera_streams.stop(camera.pk)
        camera.refresh_from_db()
        code = status.HTTP_200_OK if stopped else status.HTTP_202_ACCEPTED
        return Response({"status": camera.stream_status}, status=code)

class CameraStatusAPIView(APIView):
    permission_classes = [IsCameraAdminOrManager]
    def get(self, request, pk):
        camera = get_object_or_404(Camera, pk=pk)
        alerts = Alert.objects.filter(camera=camera, is_resolved=False).order_by("-created_at")
        active = [{"id": a.id, "alert_type": a.alert_type, "severity": a.severity,
                   "message": a.message, "created_at": a.created_at} for a in alerts]
        return Response({"status": camera.stream_status, "occupancy": camera.occupancy,
            "queue_length": camera.queue_length, "estimated_wait_time": camera.estimated_wait_time,
            "last_seen": camera.last_seen, "active_alerts": active})

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import (
    MultiPartParser,
    FormParser,
)

from branches.models import Branch
from analytics.models import LiveAnalytics, UploadedVideo


class VideoUploadAPIView(APIView):

    parser_classes = [
        MultiPartParser,
        FormParser,
    ]

    def post(self, request):

        branch_name = request.data.get(
            "branch"
        )

        video = request.FILES.get(
            "video"
        )

        if not branch_name:
            return Response(
                {"error": "Branch is required"},
                status=400
            )

        if not video:
            return Response(
                {"error": "Video is required"},
                status=400
            )

        try:

            branch = Branch.objects.get(
                branch_name=branch_name
            )

        except Branch.DoesNotExist:

            return Response(
                {"error": "Branch not found"},
                status=404
            )

        uploaded_video = UploadedVideo.objects.create(
            branch=branch,
            video_file=video,
            status="pending",
        )

        return Response({
            "message": "Video uploaded successfully",
            "video_id": uploaded_video.id,
        })


class UploadedVideosAPIView(APIView):

    def get(self, request):

        videos = UploadedVideo.objects.all().order_by(
            "-uploaded_at"
        )

        data = []

        for video in videos:

            data.append({
                "id": video.id,
                "branch": video.branch.branch_name,
                "video_file": video.video_file.name,
                "status": video.status,
                "uploaded_at": str(
                    video.uploaded_at
                ),
            })

        return Response(data)


class AnalyticsResultsAPIView(APIView):

    def get(self, request):

        results = LiveAnalytics.objects.filter(
            uploaded_video__isnull=False
        ).select_related(
            "branch",
            "uploaded_video",
        ).order_by(
            "-created_at"
        )

        data = []

        for result in results:
            video = result.uploaded_video
            data.append({
                "id": result.id,
                "video_name": video.video_file.name.replace("\\", "/").rsplit("/", 1)[-1],
                "branch": result.branch.branch_name,
                "customer_count": result.customer_count,
                "queue_length": result.queue_length,
                "average_wait_time": result.average_wait_time,
                "occupancy": result.occupancy,
                "status": video.status,
                "processed_at": (
                    video.processed_at.isoformat()
                    if video.processed_at
                    else None
                ),
            })

        return Response(data)

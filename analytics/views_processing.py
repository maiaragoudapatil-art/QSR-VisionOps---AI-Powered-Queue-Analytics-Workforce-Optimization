import logging

from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response

from analytics.models import (
    UploadedVideo,
    LiveAnalytics,
)

from analytics.video_analytics import (
    process_video,
)

from branches.models import Camera

logger = logging.getLogger(__name__)


class RunAnalyticsAPIView(APIView):

    def post(self, request):

        videos = UploadedVideo.objects.filter(
            status="pending"
        )

        processed = 0
        failed = 0

        for video in videos:

            camera = Camera.objects.filter(
                branch=video.branch
            ).first()

            if not camera:
                video.status = "failed"
                video.processed_at = timezone.now()
                video.save(update_fields=["status", "processed_at"])
                logger.error(
                    "Cannot process uploaded video %s: branch %s has no camera",
                    video.id,
                    video.branch_id,
                )
                failed += 1
                continue

            video.status = "processing"
            video.save(update_fields=["status"])

            try:
                metrics = process_video(video.video_file.path)

                LiveAnalytics.objects.create(
                    uploaded_video=video,
                    branch=video.branch,
                    camera=camera,
                    customer_count=metrics["customer_count"],
                    queue_length=metrics["queue_length"],
                    average_wait_time=metrics["average_wait_time"],
                    occupancy=metrics["occupancy"],
                )

                video.status = "completed"
                video.processed_at = timezone.now()
                video.save(update_fields=["status", "processed_at"])
                processed += 1
            except Exception:
                video.status = "failed"
                video.processed_at = timezone.now()
                video.save(update_fields=["status", "processed_at"])
                logger.exception("Failed to process uploaded video %s", video.id)
                failed += 1

        return Response({
            "message": f"{processed} videos processed; {failed} failed",
            "processed": processed,
            "failed": failed,
        })
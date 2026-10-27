from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from analytics.models import LiveAnalytics
from core.mongo import analytics_archive


class Command(BaseCommand):

    help = "Archive PostgreSQL analytics data to MongoDB"

    def handle(self, *args, **kwargs):

        cutoff = timezone.now() - timedelta(days=30)

        records = LiveAnalytics.objects.filter(
            created_at__lt=cutoff
        )

        archived_count = 0

        for item in records:
            video = item.uploaded_video if item.uploaded_video_id else None

            analytics_archive.insert_one({

                "video_name": (
                    video.video_file.name.replace("\\", "/").rsplit("/", 1)[-1]
                    if video
                    else None
                ),

                "branch": str(item.branch),

                "camera": str(item.camera),

                "customer_count":
                    item.customer_count,

                "queue_length":
                    item.queue_length,

                "average_wait_time":
                    item.average_wait_time,

                "occupancy":
                    item.occupancy,

                "postgres_created_at":
                    item.created_at.isoformat(),

                "processed_at": (
                    video.processed_at.isoformat()
                    if video and video.processed_at
                    else item.created_at.isoformat()
                ),

                "archived_at":
                    timezone.now().isoformat(),
                
                "snapshot_type": "30 Day Archived Analytics",

            })

            archived_count += 1

        records.delete()

        self.stdout.write(
            self.style.SUCCESS(
                f"{archived_count} records archived to MongoDB successfully."
            )
        )
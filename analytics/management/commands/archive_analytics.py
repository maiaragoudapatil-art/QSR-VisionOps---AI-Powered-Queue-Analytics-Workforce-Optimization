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
            evidence = [
                {"alert_id": alert.id, "alert_type": alert.alert_type,
                 "image_path": evidence.image_path, "video_path": evidence.video_path,
                 "created_at": evidence.created_at.isoformat()}
                for alert in item.camera.alert_set.all()
                for evidence in alert.evidence.all()
            ]
            snapshot_path = next(
                (entry["image_path"] for entry in evidence if entry["image_path"]),
                None,
            )
            source_video = (
                video.video_file.name
                if video
                else next((entry["video_path"] for entry in evidence if entry["video_path"]), None)
            )

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
                "snapshot_path": snapshot_path,
                "evidence_image": snapshot_path,
                "source_video": source_video,
                "evidence": evidence,

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
from analytics.models import LiveAnalytics
from core.mongo import analytics_archive


def archive_analytics():

    records = LiveAnalytics.objects.all()

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
            "created_at":
                str(item.created_at),
            "processed_at": (
                video.processed_at.isoformat()
                if video and video.processed_at
                else item.created_at.isoformat()
            ),
        })

    return records.count()
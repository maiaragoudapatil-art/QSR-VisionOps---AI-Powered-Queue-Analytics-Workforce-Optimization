from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from core.mongo import analytics_archive


def _media_url(request, path):
    if not path or path.startswith(("http://", "https://")):
        return path
    media_path = path if path.startswith("/") else f"{settings.MEDIA_URL}{path}"
    return request.build_absolute_uri(media_path)


class ArchivedAnalyticsAPIView(APIView):

    def get(self, request):

        data = list(
            analytics_archive.find(
                {},
                {"_id": 0}
            )
        )

        for record in data:
            evidence = record.get("evidence") or []
            snapshot = record.get("evidence_image") or record.get("snapshot_path")
            if not snapshot:
                snapshot = next(
                    (entry.get("image_path") for entry in evidence if entry.get("image_path")),
                    None,
                )
            video = record.get("source_video")
            if not video:
                video = next(
                    (entry.get("video_path") for entry in evidence if entry.get("video_path")),
                    None,
                )
            record["snapshot_path"] = _media_url(request, snapshot)
            record["evidence_image"] = record["snapshot_path"]
            record["source_video"] = _media_url(request, video)
            for entry in evidence:
                entry["image_path"] = _media_url(request, entry.get("image_path"))
                entry["video_path"] = _media_url(request, entry.get("video_path"))

        return Response(data)
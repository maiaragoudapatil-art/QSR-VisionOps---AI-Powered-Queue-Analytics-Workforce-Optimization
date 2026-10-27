from rest_framework.views import APIView
from rest_framework.response import Response
from core.mongo import analytics_archive


class ArchivedAnalyticsAPIView(APIView):

    def get(self, request):

        data = list(
            analytics_archive.find(
                {},
                {"_id": 0}
            )
        )

        return Response(data)
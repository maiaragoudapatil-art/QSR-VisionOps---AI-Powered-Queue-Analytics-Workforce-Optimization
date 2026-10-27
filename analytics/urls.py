from django.urls import path

from .views import (
    export_csv,
    export_pdf,
)

from .views_mongo import (
    ArchivedAnalyticsAPIView,
)

from .views_video import (
    VideoUploadAPIView,
    UploadedVideosAPIView,
    AnalyticsResultsAPIView,
)

from .views_processing import (
    RunAnalyticsAPIView,
)

urlpatterns = [

    path(
        "export-csv/",
        export_csv,
        name="export-csv",
    ),

    path(
        "export-pdf/",
        export_pdf,
        name="export-pdf",
    ),

    path(
        "archived-analytics/",
        ArchivedAnalyticsAPIView.as_view(),
        name="archived-analytics",
    ),

    path(
        "upload-video/",
        VideoUploadAPIView.as_view(),
        name="upload-video",
    ),

    path(
        "run-analytics/",
        RunAnalyticsAPIView.as_view(),
        name="run-analytics",
    ),

    path(
        "uploaded-videos/",
        UploadedVideosAPIView.as_view(),
        name="uploaded-videos",
    ),

    path(
        "analytics-results/",
        AnalyticsResultsAPIView.as_view(),
        name="analytics-results",
    ),
]
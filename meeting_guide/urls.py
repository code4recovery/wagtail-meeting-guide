from django.urls import path

from .views import (
    MeetingsReactJSView, MeetingsAPIView, RegionAPIView,
    MeetingsPrintView, MeetingsPrintDownloadView,
)

app_name = "meeting-guide"

urlpatterns = [
    path('', MeetingsReactJSView.as_view(), name="react"),
    path('api/', MeetingsAPIView.as_view(), name="api"),
    path('api/regions/', RegionAPIView.as_view(), name="region-api"),
    path('print/', MeetingsPrintView.as_view(), name="print"),
    path('download/', MeetingsPrintDownloadView.as_view(), name="download"),
]

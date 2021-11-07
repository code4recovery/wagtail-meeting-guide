from django.urls import path

from .views import MeetingsAPIView

app_name = "meeting-guide"

urlpatterns = [
    path("api/", MeetingsAPIView.as_view(), name="api"),
]

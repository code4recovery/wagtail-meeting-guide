from django.urls import path

from .views import MeetingsHomeView, MeetingsAPIView

app_name = "meeting-guide"

urlpatterns = [
    path("", MeetingsHomeView.as_view(), name="home"),
    path("api/", MeetingsAPIView.as_view(), name="api"),
]

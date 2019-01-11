from django.urls import path

from .views import MeetingsReactJSView, MeetingsAPIView


app_name = "meeting-guide"

urlpatterns = [
    path('', MeetingsReactJSView.as_view(), name="react"),
    path('api/', MeetingsAPIView.as_view(), name="api"),
]

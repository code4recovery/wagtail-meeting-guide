from django.urls import path

from .views import MeetingsReactJSView, MeetingsAPIView


urlpatterns = [
    path('', MeetingsReactJSView.as_view(), name="react"),
    path('api/', MeetingsAPIView.as_view(), name="api"),
]

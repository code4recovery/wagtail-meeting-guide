import datetime
import json
import re

from django.conf import settings
from django.http import HttpResponse
from django.middleware.gzip import GZipMiddleware
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import TemplateView

from django_weasyprint import WeasyTemplateResponseMixin

from .models import Meeting, MeetingType, Region
from .settings import get_meeting_guide_settings


@method_decorator(
    cache_page(3600 * 24 * 7, key_prefix="wagtail_meeting_guide_api_cache"),
    name='dispatch',
)
class MeetingsBaseView(TemplateView):
    DAY_OF_WEEK = (
        (0, "Sunday"),
        (1, "Monday"),
        (2, "Tuesday"),
        (3, "Wednesday"),
        (4, "Thursday"),
        (5, "Friday"),
        (6, "Saturday"),
    )

    def get_meetings(self):
        return (
            Meeting.objects.live().filter(
                status=Meeting.ACTIVE,
            ).select_related("meeting_location", "group").prefetch_related(
                "meeting_location__region",
                # 'types',  # ParentalManyToManyField instead of ManyToManyField causes Django to throw up on this
            ).order_by("day_of_week", "start_time")
        )


class MeetingsHomeView(TemplateView):
    """
    List all meetings in the Meeting Guide ReactJS plugin.
    """

    template_name = "meeting_guide/meetings_home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        settings = get_meeting_guide_settings()
        context["settings"] = json.dumps(settings)
        context["mapbox_key"] = settings["map"]["key"]
        context["timezone"] = settings["timezone"]

        return context


class MeetingsAPIView(MeetingsBaseView):
    """
    Return a JSON response of the meeting list.
    """

    def get(self, request, *args, **kwargs):
        meetings = self.get_meetings()
        meetings_dict = []

        # Eager load all regions to reference below.
        regions = Region.objects.all().prefetch_related("children")

        for meeting in meetings:
            meeting_types = list(
                meeting.types.values_list("spec_code", flat=True)
            )

            group_info = ""
            if len(meeting.district):
                location = f"{meeting.meeting_location.title} (D{meeting.district})"
                group_info = f"D{meeting.district}"
            else:
                location = meeting.meeting_location.title

            gso_number = getattr(meeting.group, "gso_number", None)
            if gso_number and len(gso_number):
                group_info += f" / GSO #{gso_number}"

            region_ancestors = list(
                regions.get(id=meeting.meeting_location.region.id)
                .get_ancestors(include_self=True)
                .values_list("name", flat=True)
            )

            notes = meeting.details

            meeting_dict = {
                "name": meeting.title,
                "slug": meeting.slug,
                "notes": notes,
                "updated": f"{meeting.last_published_at if meeting.last_published_at else datetime.datetime.now():%Y-%m-%d %H:%M:%S}",
                "url": f"{settings.BASE_URL}/meetings/?meeting={meeting.slug}",
                "day": meeting.day_of_week,
                "time": f"{meeting.start_time:%H:%M}",
                "end_time": f"{meeting.end_time:%H:%M}",
                "conference_url": meeting.conference_url,
                "conference_phone": meeting.conference_phone,
                "types": meeting_types,
                "location": location,
                "formatted_address": meeting.meeting_location.formatted_address,
                "latitude": meeting.meeting_location.lat,
                "longitude": meeting.meeting_location.lng,
                "regions": region_ancestors,
                "group": group_info,
            }

            if len(meeting.paypal):
                meeting_dict["paypal"] = f"https://paypal.me/{meeting.paypal}"

            if len(meeting.venmo):
                meeting_dict["venmo"] = meeting.venmo

            if "feedback_url" in settings.MEETING_GUIDE:
                meeting_dict["feedback_url"] = settings.MEETING_GUIDE["feedback_url"]

            meetings_dict.append(meeting_dict)

        response = GZipMiddleware().process_response(
            request,
            HttpResponse(json.dumps(meetings_dict), content_type="application/json")
        )

        return response

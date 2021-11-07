import datetime
import json
import re

from django.conf import settings
from django.http import HttpResponse
from django.middleware.gzip import GZipMiddleware
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import TemplateView

from .models import Meeting, Region, Location


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
            Meeting.objects.live()
            .filter(status=Meeting.ACTIVE)
            .select_related("group")
            .order_by("day_of_week", "start_time")
        )


class MeetingsAPIView(MeetingsBaseView):
    """
    Return a JSON response of the meeting list.
    """

    def get(self, request, *args, **kwargs):
        meetings = self.get_meetings()
        meetings_dict = []

        # Eager load all regions and locations to reference below.
        regions = Region.objects.all().prefetch_related("children")
        locations = {}
        for location in Location.objects.all():
            locations[location.id] = location

        for meeting in meetings:
            meeting_types = list(
                meeting.types.values_list("spec_code", flat=True)
            )

            # We need to get the Location object
            location = locations[meeting.get_parent().id]

            group_info = ""
            if len(meeting.district):
                location_title = f"{location.title} (D{meeting.district})"
                group_info = f"D{meeting.district}"
            else:
                location_title = location.title

            gso_number = getattr(meeting.group, "gso_number", None)
            if gso_number and len(gso_number):
                group_info += f" / GSO #{gso_number}"

            region_ancestors = list(
                regions.get(id=location.region.id)
                .get_ancestors(include_self=True)
                .values_list("name", flat=True)
            )

            notes = meeting.details

            meetings_dict.append(
                {
                    "name": meeting.title,
                    "slug": meeting.slug,
                    "notes": notes,
                    "updated": f"{meeting.last_published_at if meeting.last_published_at else datetime.datetime.now():%Y-%m-%d %H:%M:%S}",
                    "url": f"{settings.BASE_URL}{meeting.url_path}",
                    "day": meeting.day_of_week,
                    "time": f"{meeting.start_time:%H:%M}",
                    "end_time": f"{meeting.end_time:%H:%M}",
                    "conference_url": meeting.conference_url,
                    "conference_phone": meeting.conference_phone,
                    "types": meeting_types,
                    "location": location_title,
                    "formatted_address": location.formatted_address,
                    "latitude": location.lat,
                    "longitude": location.lng,
                    "regions": region_ancestors,
                    "group": group_info,
                    "paypal": f"https://paypal.me/{meeting.paypal}" if len(meeting.paypal) else "",
                    "venmo": meeting.venmo,
                }
            )

        response = GZipMiddleware().process_response(
            request,
            HttpResponse(json.dumps(meetings_dict), content_type="application/json")
        )

        return response

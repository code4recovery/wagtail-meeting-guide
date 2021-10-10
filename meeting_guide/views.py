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


class MeetingsReactJSView(TemplateView):
    """
    List all meetings in the Meeting Guide ReactJS plugin.
    """

    template_name = "meeting_guide/meetings_list_react.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["settings"] = json.dumps(get_meeting_guide_settings())

        return context


class MeetingsDataTablesView(MeetingsBaseView):
    """
    List all meetings in a jQuery datatable.
    """

    template_name = "meeting_guide/meetings_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["meetings"] = self.get_meetings()

        return context


class MeetingsPrintView(TemplateView):
    """
    List all meetings in an HTML printable format.
    """

    template_name = "meeting_guide/meetings_list_print.html"

    def get_meetings(self):
        return (
            Meeting.objects.live().select_related(
                "meeting_location__region__parent", "group",
            ).filter(status__gte=1)
            .order_by(
                "day_of_week",
                "meeting_location__region__parent__name",
                "meeting_location__postal_code",
                "start_time",
            )
        )  # [0:10]

    def get_context_data(self, **kwargs):
        meetings = self.get_meetings()
        meeting_dict = {}

        slice_address = re.compile(r"(.*), PA [0-9]+, USA")

        for m in meetings:
            day = m.get_day_of_week_display()
            region = m.meeting_location.region.parent.name
            postal_code = m.meeting_location.postal_code
            types = list(m.types.values_list("intergroup_code", flat=True))

            if region not in meeting_dict:
                meeting_dict[region] = {}
            if day not in meeting_dict[region]:
                meeting_dict[region][day] = {}
            if postal_code not in meeting_dict[region][day]:
                meeting_dict[region][day][postal_code] = []

            group_address = re.match(
                slice_address, m.meeting_location.formatted_address
            )

            if group_address and group_address.group(1):
                formatted_address = group_address.group(1).split(",")[0]
            else:
                formatted_address = m.meeting_location.formatted_address

            meeting_dict[region][day][postal_code].append(
                {
                    "name": m.title,
                    "time_formatted": f"{m.start_time:%I:%M%p}",
                    "day": day,
                    "types": types,
                    "location": m.meeting_location.title,
                    "formatted_address": formatted_address,
                    "group": getattr(m.group, "name", None),
                    "district": m.district,
                    "gso_number": getattr(m.group, "gso_number", None),
                    "meeting_details": m.details,
                    "location_details": m.meeting_location.details,
                }
            )

        context = super().get_context_data(**kwargs)
        context["meetings"] = meeting_dict
        context["meeting_types"] = (
            MeetingType.objects.values("type_name", "intergroup_code")
            .filter(intergroup_code__isnull=False)
            .order_by("display_order", "intergroup_code")
        )

        return context


class MeetingsPrintDownloadView(WeasyTemplateResponseMixin, MeetingsPrintView):
    """
    Provide a PDF download of all active meetings, sourcing
    the HTML printable format.

    SEPIA WIDTH: 3.75" x 5.5" papersize (0.25" margin)
    """

    from django.contrib.staticfiles import finders

    meeting_guide_css_file = finders.find("meeting_guide/print.css")

    pdf_stylesheets = [meeting_guide_css_file]
    pdf_presentational_hints = True


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
                    "location": location,
                    "formatted_address": meeting.meeting_location.formatted_address,
                    "latitude": meeting.meeting_location.lat,
                    "longitude": meeting.meeting_location.lng,
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


class RegionAPIView(MeetingsBaseView):
    """
    Return a JSON response of the meeting list.
    """

    def get(self, request, *args, **kwargs):
        tree = get_region_tree()
        return HttpResponse(json.dumps(tree), content_type="application/json")


from django.views.generic.edit import UpdateView

from .models import Location


class LocationUpdate(UpdateView):
    model = Location
    fields = ["title", "address1", "address2", "city", "state", "postal_code"]

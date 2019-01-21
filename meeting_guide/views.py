import datetime
import json

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.cache import cache_page
from django.views.generic import TemplateView

from .models import Meeting


class CacheMixin(object):
    cache_timeout = 3600 * 24 * 7

    def get_cache_timeout(self):
        return self.cache_timeout

    def dispatch(self, *args, **kwargs):
        return cache_page(self.get_cache_timeout())(super(CacheMixin, self).dispatch)(*args, **kwargs)


class MeetingsBaseView(CacheMixin, TemplateView):
    DAY_OF_WEEK = (
        (0, 'Sunday'),
        (1, 'Monday'),
        (2, 'Tuesday'),
        (3, 'Wednesday'),
        (4, 'Thursday'),
        (5, 'Friday'),
        (6, 'Saturday'),
    )

    def get_meetings(self):
        return Meeting.objects.filter(
            status=1,
        ).select_related(
            'meeting_location',
            'group',
        ).prefetch_related(
            'meeting_location__region',
            # 'types',  # ParentalManyToManyField instead of ManyToManyField causes Django to throw up on this
        ).order_by(
            'day_of_week',
            'start_time',
        )


class MeetingsReactJSView(CacheMixin, TemplateView):
    """
    List all meetings in the Meeting Guide ReactJS plugin.
    """
    template_name = 'meeting_guide/meetings_list_react.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mapbox_key'] = "pk.eyJ1IjoiZmxpcHBlcnBhIiwiYSI6ImNqcHZhbjZwdDBldDA0MXBveTlrZG9uaGIifQ.WpB5eRUcUnQh0-P_CX3nKg"
        return context


class MeetingsDataTablesView(MeetingsBaseView):
    """
    List all meetings in a jQuery datatable.
    """
    template_name = 'meeting_guide/meetings_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['meetings'] = self.get_meetings()

        return context


class MeetingsAPIView(MeetingsBaseView):
    """
    Return a JSON response of the meeting list.
    """

    def get(self, request, *args, **kwargs):
        meetings = self.get_meetings()

        meetings_dict = []

        for meeting in meetings:
            meetings_dict.append({
                "id": meeting.id,
                "name": meeting.title,
                "slug": meeting.slug,
                "notes": meeting.meeting_details,
                "updated": f"{meeting.last_published_at if meeting.last_published_at else datetime.datetime.now():%Y-%m-%d %H:%M:%S}",
                "location_id": meeting.meeting_location.id,
                "url": "https://www.disney.com/",
                "time": f"{meeting.start_time:%H:%M}",
                "end_time": f"{meeting.end_time:%H:%M}",
                "time_formatted": f"{meeting.start_time:%H:%M %P}",
                "distance": "",
                "day": meeting.day_of_week,
                "types": list(meeting.types.values_list('meeting_guide_code', flat=True)),
                "location": meeting.meeting_location.title,
                "location_notes": "",
                "location_url": "https://www.disney.com/",
                "formatted_address": meeting.meeting_location.formatted_address,
                "latitude": str(meeting.meeting_location.lat),
                "longitude": str(meeting.meeting_location.lng),
                "region_id": meeting.meeting_location.region.id,
                "region": f"{meeting.meeting_location.region.parent.name}: {meeting.meeting_location.region.name}",

                "group": meeting.group.name if meeting.group else '',
                "image": "",
            })

            """
            Eventually, we'll support regions and subregions:
                "region_id": meeting.meeting_location.region.parent.id,
                "region": meeting.meeting_location.region.parent.name,
                "sub_region_id": meeting.meeting_location.region.id,
                "sub_region": meeting.meeting_location.region.name,
            """

        if settings.DEBUG:
            meetings_dict = json.dumps(meetings_dict, indent=4)
        else:
            meetings_dict = json.dumps(meetings_dict)

        return HttpResponse(meetings_dict, content_type='application/json')


from django.views.generic.edit import UpdateView

from .models import Location


class LocationUpdate(UpdateView):
    model = Location
    fields = ['title', 'address1', 'address2', 'city', 'state', 'postal_code']

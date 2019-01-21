import datetime

from django.db import models
from django.forms import CheckboxSelectMultiple
from django.utils.functional import cached_property

from modelcluster.fields import ParentalManyToManyField
from wagtail.core.models import Page
from wagtail.admin.edit_handlers import (
    FieldPanel, MultiFieldPanel, FieldRowPanel, HelpPanel
)
from wagtail.search.index import SearchField
from wagtailgeowidget.edit_handlers import GeoPanel
from wagtailgeowidget.helpers import geosgeometry_str_to_struct


class Region(models.Model):
    """
    Tree of regions and sub-regions.
    """

    name = models.CharField(max_length=255)
    parent = models.ForeignKey(
        "Region", blank=True, null=True, on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ("name", "parent")
        ordering = ["parent__name", "name"]
        indexes = [models.Index(fields=["name"])]

    def __str__(self):
        if self.parent is None:
            parent_name = ""
        else:
            parent_name = f"{self.parent.name}: "

        return f"{parent_name}{self.name}"


class Group(models.Model):
    """
    Model for storing group data.
    """

    STATUS_CHOICES = ((0, "Inactive"), (1, "Active"))

    name = models.CharField(max_length=255)
    gso_number = models.CharField(max_length=10, null=True, blank=True)
    district = models.CharField(max_length=10, null=True, blank=True)
    area = models.CharField(max_length=10, null=True, blank=True)
    status = models.SmallIntegerField(default=1, choices=STATUS_CHOICES)
    founded = models.DateField(null=True, blank=True)
    history = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return "{0}".format(self.name)


class GroupContribution(models.Model):
    """
    For keeping track of contributions from groups.
    """

    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    date = models.DateField(default=datetime.date.today)
    amount = models.DecimalField(max_digits=20, decimal_places=2)

    class Meta:
        ordering = ["group__name", "-date"]

    def __str__(self):
        return "{0} ({1}: ${2})".format(self.group, self.date, self.amount)


class Location(Page):
    """
    Geocoded location details.
    """

    region = models.ForeignKey(Region, null=True, on_delete=models.SET_NULL)
    formatted_address = models.CharField(
        "Full Address",
        max_length=255,
        blank=True,
        null=True,
    )
    lat_lng = models.CharField(
        "Latitude/Longitude",
        max_length=255,
        blank=True,
        null=True,
    )

    @cached_property
    def point(self):
        return geosgeometry_str_to_struct(self.lat_lng)

    @property
    def lat(self):
        return self.point['y']

    @property
    def lng(self):
        return self.point['x']

    content_panels = Page.content_panels + [
        FieldPanel("region"),
        MultiFieldPanel(
            [
                FieldPanel('formatted_address'),
                GeoPanel('lat_lng', address_field='formatted_address'),
            ],
            'Geocoded Address',
        ),
    ]

    search_fields = Page.search_fields + [
        SearchField("region", partial_match=True),
        SearchField("formatted_address", partial_match=True),
    ]

    subpage_types = ["Meeting"]

    class Meta:
        indexes = [
            models.Index(fields=["region"]),
            models.Index(fields=["formatted_address"]),
        ]

    def __str__(self):
        return "{0}: {1}".format(self.region, self.title)


class MeetingType(models.Model):
    """
    Model for storing different types of meetings.
    """

    type_name = models.CharField(max_length=191)
    intergroup_code = models.CharField(max_length=5, null=True, blank=True)
    meeting_guide_code = models.CharField(max_length=5, null=True, blank=True)

    class Meta:
        ordering = ["type_name"]
        indexes = [
            models.Index(fields=["type_name"]),
            models.Index(fields=["intergroup_code"]),
            models.Index(fields=["meeting_guide_code"]),
        ]

    def __str__(self):
        return "{0} ({1} / {2})".format(
            self.type_name,
            self.intergroup_code,
            self.meeting_guide_code,
        )


class Meeting(Page):
    """
    Model for storing meeting data.
    """

    DAY_OF_WEEK = (
        (0, "Sunday"),
        (1, "Monday"),
        (2, "Tuesday"),
        (3, "Wednesday"),
        (4, "Thursday"),
        (5, "Friday"),
        (6, "Saturday"),
    )

    STATUS_CHOICES = ((0, "Inactive"), (1, "Active"))

    group = models.ForeignKey(
        Group, null=True, blank=True, on_delete=models.SET_NULL, related_name="meetings"
    )
    meeting_location = models.ForeignKey(
        Location, null=True, on_delete=models.SET_NULL, related_name="meetings"
    )
    start_time = models.TimeField(null=True)
    end_time = models.TimeField(null=True)
    day_of_week = models.SmallIntegerField(default=0, choices=DAY_OF_WEEK)
    status = models.SmallIntegerField(default=1, choices=STATUS_CHOICES)
    meeting_details = models.TextField(
        help_text="Additional details for the meeting.", null=True, blank=True
    )
    types = ParentalManyToManyField(
        MeetingType,
        related_name="meetings",
        limit_choices_to={'intergroup_code__isnull': False},
    )

    @property
    def day_sort_order(self):
        """
        Returns 0 for today's day of the week, up to 6 for yesterday's day of the
        week rather than Sunday - Saturday.
        """
        day_sort_order = self.day_of_week - datetime.datetime.today().weekday() - 1
        if day_sort_order < 0:
            day_sort_order += 7

        return day_sort_order

    content_panels = Page.content_panels + [
        FieldPanel("group"),
        FieldRowPanel(
            [
                FieldPanel("day_of_week"),
                FieldPanel("start_time"),
                FieldPanel("end_time"),
            ]
        ),
        HelpPanel(content=""),
        FieldPanel("types", widget=CheckboxSelectMultiple),
        FieldPanel("meeting_details"),
    ]

    search_fields = Page.search_fields + [
        SearchField("group", partial_match=True),
        SearchField("meeting_location", partial_match=True),
    ]

    parent_page_types = ["Location"]

    class Meta:
        indexes = [
            models.Index(fields=["meeting_location"]),
            models.Index(fields=["day_of_week"]),
        ]

    def save(self, *args, **kwargs):
        self.meeting_location = Location.objects.get(pk=self.get_parent().id)
        super(Meeting, self).save(*args, **kwargs)

    def __str__(self):
        return "{0} ({1}): {2} @ {3}".format(
            self.title, self.group, self.day_of_week, self.start_time
        )

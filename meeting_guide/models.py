import datetime

from django.core.validators import MinLengthValidator
from django.db import models
from django.forms import CheckboxSelectMultiple
from django.utils.functional import cached_property

from modelcluster.fields import ParentalManyToManyField
from mptt.models import MPTTModel, TreeForeignKey
from wagtail.core.models import Page
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel, FieldRowPanel
from wagtail.search.index import SearchField
from wagtailgeowidget.edit_handlers import GeoPanel
from wagtailgeowidget.helpers import geosgeometry_str_to_struct

from .validators import (
    CashAppUsernameValidator,
    ConferencePhoneValidator,
    PayPalUsernameValidator,
    VenmoUsernameValidator,
)


class Region(MPTTModel):
    """
    Tree of regions and sub-regions.
    """

    name = models.CharField(max_length=255)
    parent = TreeForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children"
    )

    def __str__(self):
        ancestors = self.get_ancestors(include_self=True).values_list("name", flat=True)
        return " > ".join(ancestors)

    class MPTTMeta:
        order_insertion_by = ["name"]


class Group(models.Model):
    """
    Model for storing group data.
    """

    STATUS_CHOICES = ((0, "Inactive"), (1, "Active"))

    name = models.CharField(max_length=255)
    gso_number = models.CharField(max_length=10, null=True, blank=True)
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

    region = models.ForeignKey(
        Region,
        related_name="locations",
        on_delete=models.PROTECT,
        limit_choices_to={"parent__isnull": False},
    )
    formatted_address = models.CharField(
        "Full Address", max_length=255, blank=True, null=True
    )
    lat_lng = models.CharField(
        "Latitude/Longitude", max_length=255, blank=True, null=True
    )
    postal_code = models.CharField("Postal Code", max_length=12, blank=True)
    details = models.TextField(
        null=True,
        blank=True,
        help_text="Details specific to the location, not the meeting. For example, "
        "'Located in shopping center behind the bank.'",
    )

    @cached_property
    def point(self):
        return geosgeometry_str_to_struct(self.lat_lng)

    @property
    def lat(self):
        return self.point["y"]

    @property
    def lng(self):
        return self.point["x"]

    content_panels = Page.content_panels + [
        FieldPanel("region"),
        FieldPanel("postal_code"),
        FieldPanel("details"),
        MultiFieldPanel(
            [
                FieldPanel("formatted_address"),
                GeoPanel("lat_lng", address_field="formatted_address"),
            ],
            "Geocoded Address",
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
    Model for storing different types of meetings. Initially populating with data from:
    https://github.com/code4recovery/spec
    """

    type_name = models.CharField(max_length=191)
    intergroup_code = models.CharField(max_length=5, null=True, blank=True)
    spec_code = models.CharField(max_length=5, null=True, blank=True)
    display_order = models.PositiveSmallIntegerField(default=100)

    class Meta:
        ordering = ["display_order", "type_name"]
        indexes = [
            models.Index(fields=["type_name"]),
            models.Index(fields=["intergroup_code"]),
            models.Index(fields=["spec_code"]),
        ]

    def __str__(self):
        return "{0} ({1} / {2})".format(
            self.type_name, self.intergroup_code, self.spec_code
        )


class Meeting(Page):
    """
    Model for storing meeting data.
    """

    SUNDAY = 0
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    DAY_OF_WEEK = (
        (SUNDAY, "Sunday"),
        (MONDAY, "Monday"),
        (TUESDAY, "Tuesday"),
        (WEDNESDAY, "Wednesday"),
        (THURSDAY, "Thursday"),
        (FRIDAY, "Friday"),
        (SATURDAY, "Saturday"),
    )

    INACTIVE = 0
    ACTIVE = 1
    STATUS_CHOICES = (
        (ACTIVE, "Active"),
        (INACTIVE, "Inactive Permanently"),
    )

    group = models.ForeignKey(
        Group, null=True, blank=True, on_delete=models.SET_NULL, related_name="meetings"
    )
    meeting_location = models.ForeignKey(
        Location, related_name="meetings", null=True, on_delete=models.SET_NULL
    )
    start_time = models.TimeField(null=True)
    end_time = models.TimeField(null=True)
    day_of_week = models.SmallIntegerField(default=0, choices=DAY_OF_WEEK)
    status = models.SmallIntegerField(default=1, choices=STATUS_CHOICES)
    details = models.TextField(
        null=True, blank=True, help_text="Additional details about the meeting."
    )
    area = models.CharField(max_length=10, blank=True)
    district = models.CharField(max_length=10, blank=True)
    types = ParentalManyToManyField(
        MeetingType,
        related_name="meetings",
        limit_choices_to={"intergroup_code__isnull": False},
    )
    conference_url = models.URLField(
        blank=True,
        verbose_name="Conference URL",
        default="",
        help_text="Example: " \
            "https://zoom.com/j/123456789?pwd=ExzUZMeT091pRU0Omc2QWjErUUUpxS1B",
    )
    conference_phone = models.CharField(
        max_length=255,
        blank=True,
        default="",
        validators=[ConferencePhoneValidator()],
        help_text="Enter a valid conference phone number. The three groups of " \
            "numbers in this example are a Zoom phone number, meeting code, and " \
            "password: +19294362866,,2151234215#,,#,,12341234#",
    )
    venmo = models.TextField(
        max_length=31,  # Venmo's max username length is 31 chars with the "@" prefix
        validators=[VenmoUsernameValidator()],
        blank=True,
        verbose_name="Venmo Account",
        default="",
        help_text="Example: @aa-mygroup",
    )
    paypal = models.TextField(
        blank=True,
        verbose_name="PayPal Username",
        default="",
        max_length=255,
        validators=[PayPalUsernameValidator(), MinLengthValidator(3)],
        help_text="Example: aamygroup",
    )
    cashapp = models.TextField(
        max_length=31,  # Venmo's max username length is 31 chars with the "@" prefix
        validators=[CashAppUsernameValidator()],
        blank=True,
        verbose_name="CashApp Account",
        default="",
        help_text="Example: $aa-mygroup",
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
        FieldRowPanel(
            [
                FieldPanel("day_of_week"),
                FieldPanel("start_time"),
                FieldPanel("end_time"),
            ],
        ),
        FieldRowPanel(
            [
                FieldPanel("group"),
                FieldPanel("status"),
            ],
        ),
        FieldRowPanel(
            [
                FieldPanel("area"),
                FieldPanel("district"),
            ],
        ),
        FieldRowPanel(
            [
                FieldPanel("venmo"),
                FieldPanel("paypal"),
            ],
        ),
        FieldRowPanel(
            [
                FieldPanel("conference_url"),
                FieldPanel("conference_phone"),
            ],
        ),
        FieldPanel("types", widget=CheckboxSelectMultiple),
        FieldPanel("details"),
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
        """
        Associate the meeting with the Location parent and save. Then
        automatically assign the ONLINE meeting type if the field is
        populated.
        """
        # Associate with the parent meeting location, and save in case this
        # is new, before we change meeting types.
        self.meeting_location = Location.objects.get(pk=self.get_parent().id)

        # Automagically add or remove the online meeting type.
        online_meeting_type = MeetingType.objects.get(spec_code="ONL")
        if self.conference_url:
            self.types.add(online_meeting_type)
        else:
            self.types.remove(online_meeting_type)

        super().save(*args, **kwargs)

    def __str__(self):
        return "{0} ({1}): {2} @ {3}".format(
            self.title, self.group, self.day_of_week, self.start_time
        )

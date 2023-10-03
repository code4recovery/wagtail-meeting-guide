from django.core.cache import cache
from django_filters import ModelChoiceFilter

from wagtail.admin.filters import WagtailFilterSet
from wagtail.signals import page_published
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet, SnippetViewSetGroup

from .models import Group, GroupContribution, MeetingType, Region, Location, Meeting


def receiver(sender, **kwargs):
    """
    Clear the API cache whenever a Location or Meeting is published.
    """
    cache.delete("wagtail_meeting_guide_api_cache")


# Register the signal receive for Location and Meeting publishes.
page_published.connect(receiver, sender=Location)
page_published.connect(receiver, sender=Meeting)


class RegionFilter(WagtailFilterSet):
    parent = ModelChoiceFilter(
        queryset=Region.objects.filter(parent__isnull=True),
        label='Select Region'
    )

    class Meta:
        model = Region
        fields = []


class MeetingTypeAdmin(SnippetViewSet):
    model = MeetingType
    menu_label = "Meeting Types"
    menu_icon = "folder-open-1"
    add_to_settings_menu = True
    list_display = (
        "type_name",
        "intergroup_code",
        "spec_code",
        "display_order",
    )
    ordering = ("display_order", "type_name")
    search_fields = ("type_name",)


class RegionAdmin(SnippetViewSet):
    model = Region
    menu_icon = "doc-full-inverse"
    empty_value_display = "-----"
    list_display = ("parent", "name")
    ordering = ("parent", "name")
    filterset_class = RegionFilter


class GroupAdmin(SnippetViewSet):
    model = Group
    menu_label = "Groups"
    menu_icon = "folder-open-inverse"
    add_to_settings_menu = False
    list_display = ("name", "gso_number")
    search_fields = ("name",)


class GroupContributionAdmin(SnippetViewSet):
    model = GroupContribution
    menu_label = "Contributions"
    menu_icon = "folder-open-inverse"
    add_to_settings_menu = False
    list_display = ("group", "date", "amount")
    list_filter = ("group",)
    search_fields = ("group",)


class MeetingGuideAdminGroup(SnippetViewSetGroup):
    menu_label = "Meeting Guide"
    menu_icon = "calendar-alt"
    menu_order = 1000
    items = (MeetingTypeAdmin, RegionAdmin, GroupAdmin, GroupContributionAdmin)


register_snippet(MeetingGuideAdminGroup)

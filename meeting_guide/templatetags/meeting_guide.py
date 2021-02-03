from json import dumps as json_dumps

from django import template

from meeting_guide.settings import get_meeting_guide_settings

register = template.Library()


@register.inclusion_tag("meeting_guide/tags/meeting_guide.html", takes_context=True)
def meeting_guide(context):
    """
    Display the ReactJS drive Meeting Guide list.
    """
    meeting_guide_settings = json_dumps(get_meeting_guide_settings())

    return {
        "meeting_guide_settings": meeting_guide_settings,
    }

from django import template

register = template.Library()


@register.inclusion_tag(
    'meeting_guide/tags/meeting_guide_react.html',
    takes_context=True
)
def meetings_list(context):
    """
    Display the ReactJS drive Meeting Guide list.
    """
    return {
        'mapbox_key': context['mapbox_key'],
    }

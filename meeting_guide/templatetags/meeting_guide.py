from django import template

register = template.Library()


@register.inclusion_tag(
    'meeting_guide/tags/meeting_guide.html',
    takes_context=True
)
def meeting_guide(context):
    """
    Display the ReactJS drive Meeting Guide list.
    """
    return {
        'mapbox_key': context['mapbox_key'],
    }

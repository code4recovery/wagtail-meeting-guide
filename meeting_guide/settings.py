from django.conf import settings


def get_print_options():
    """
    Default options for PDF printing.
    """

    return getattr(
        settings,
        "WAGTAIL_MEETING_GUIDE_PRINT_OPTIONS",
        {
            'page-width': '100mm',
            'page-height': '120mm',
            'margin-top': '10mm',
            'margin-right': '10mm',
            'margin-bottom': '10mm',
            'margin-left': '10mm',
            'header-left': '[section]: [subsection]',
            'encoding': "UTF-8",
            'no-outline': None
        },
    )

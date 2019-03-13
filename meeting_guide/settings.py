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
            'no-outline': None,
        },
    )


def get_print_styles():
    """
    Default options for PDF styling.
    """

    return getattr(
        settings,
        "WAGTAIL_MEETING_GUIDE_PRINT_STYLES",
        """
html, td {
  font-family: Arial, Helvetica, sans-serif;
  font-size: 9px;
  -webkit-text-size-adjust:100%;
  -ms-text-size-adjust:100%;
}

body {
  margin:0;
}

h1, .h1 {
  font-size: 24px;
}

h2, .h2 {
  font-size: 18px;
}

h3, .h3 {
  font-size: 14px;
}

h4, .h4 {
  font-size: 12px;
}

h5, .h5 {
  font-size: 11px;
}

h6, .h6 {
  font-size: 9px;
}
        """,
    )

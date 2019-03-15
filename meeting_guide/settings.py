from django.conf import settings


def get_print_options():
    """
    Default options for PDF printing.
    """

    return getattr(
        settings,
        "WAGTAIL_MEETING_GUIDE_PRINT_OPTIONS",
        {
            'page-size': 'letter',

            'margin-top': '0.5in',
            'margin-right': '0.5in',
            'margin-bottom': '0.5in',
            'margin-left': '0.5in',

            'header-left': '[section]: [subsection]',
            'header-font-name': 'Arial, sans-serif',
            'header-font-size': '20',
            'header-line': '',
            'footer-center': '[page] / [topage]',

            'quiet': '',
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
  font-size: 14pt;
  -webkit-text-size-adjust: 100%;
  -ms-text-size-adjust: 100%;
}

table {
    width: 100%;
}

body {
  margin:0;
}

.region {
    page-break-inside: avoid;
}

.page-break {
  page-break-after: always;
}

h1, .h1 {
  font-size: 1px;
}

h2, .h2 {
  font-size: 24pt;
}

h3, .h3 {
  font-size: 16pt;
}

h4, .h4 {
  font-size: 12pt;
}

h5, .h5 {
  font-size: 11pt;
}

h6, .h6 {
  font-size: 9pt;
}
        """,
    )

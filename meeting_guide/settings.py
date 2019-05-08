from django.conf import settings


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
  font-size: 11pt;
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
  font-size: 1px;
}

h3, .h3 {
  font-size: 16pt;
  display: inline-block;
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

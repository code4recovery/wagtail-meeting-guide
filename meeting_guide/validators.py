from django.core import validators
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


@deconstructible
class CashAppUsernameValidator(validators.RegexValidator):
    """
    Validator for CashApp usernames (from Square).
    - Must start with "$"
    - Only ASCII alphanumeric characters, hyphens, and underscores are supported.
    """
    regex = r"^\$[a-zA-Z0-9_-]+$"
    message = _(
        "Enter a valid CashApp username. Must start with '$', and can contain "
        "letters, numbers, '-', and '_'."
    )
    flags = 0


@deconstructible
class ConferencePhoneValidator(validators.RegexValidator):
    """
    Only allow valid characters for conference phone numbers.
    - Only numeric, "+", ",", and "#" characters are allowed.
    """
    regex = r'^[0-9+,#]+$'
    message = _(
        "Enter a valid conference phone number. The three groups of numbers in this "
        "example are a Zoom phone number, meeting code, and password: "
        "+19294362866,,2151234215#,,#,,12341234#"
    )
    flags = 0


@deconstructible
class PayPalUsernameValidator(validators.RegexValidator):
    """
    Validator for PayPal usernames.
    - 8-16 characters
    - Only ASCII alphanumeric characters are supported.
    """
    regex = r'^[a-zA-Z0-9]+$'
    message = _(
        "Enter a valid PayPal username for https://paypal.me/. Only letters and "
        "numbers are valid."
    )
    flags = 0


@deconstructible
class VenmoUsernameValidator(validators.RegexValidator):
    """
    Validator for Venmo usernames.
    - Must start with "@"
    - Only ASCII alphanumeric characters, hyphens, and underscores are supported.
    """
    regex = r"^@[a-zA-Z0-9_-]+$"
    message = _(
        "Enter a valid Venmo username. Must start with '@', and can contain letters, "
        "numbers, '-', and '_'."
    )
    flags = 0

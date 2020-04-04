from django.core import validators
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


@deconstructible
class VenmoUsernameValidator(validators.RegexValidator):
    """
    Validator for Venmo usernames.
    - Must start with "@"
    - Only ASCII alphanumeric characters, hyphens, and underscores are supported.
    """
    regex = r'^@[a-zA-Z0-9_-]+$'
    message = _(
        'Enter a valid Venmo username. Must start with "@", and can contain letters, '
        'numbers, "-", and "_".'
    )
    flags = 0

from django.core.exceptions import ValidationError
from E_Shop_API.E_Shop_Users.tests.helpers.error_messages import ErrorMessages


def validate_negative(value):
    """ Validator function to check the product price/count and set the 'active' field accordingly """
    if value < 0:
        raise ValidationError(ErrorMessages.NEGATIVE_VALUE)
    elif value == 0:
        active = False
    else:
        active = True
    return active

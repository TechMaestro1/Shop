import re
from datetime import datetime, date
from django.core.exceptions import ValidationError

from E_Shop_API.E_Shop_Users.tests.helpers.error_messages import ErrorMessages


def validate_password(value):
    """ Password validator """
    error_messages = []

    if not re.search("[A-Z]", value):
        error_messages.append(ErrorMessages.UPPER_CASE_LETTER)
    if not re.search("[0-9]", value):
        error_messages.append(ErrorMessages.AT_LEAST_ONE_DIGIT)
    if len(value) < 8:
        error_messages.append(ErrorMessages.MIN_8_CHARACTERS)
    if error_messages:
        raise ValidationError(error_messages)


def birthday_validator(value):
    """Birthday Validator"""
    error_messages = []

    today = date.today()
    if value > today:
        error_messages.append(ErrorMessages.CANNOT_BE_FUTURE)

    if value < datetime.strptime('1970-01-01', "%Y-%m-%d").date():
        error_messages.append(ErrorMessages.YEAR_IS_NOT_VALID)

    if error_messages:
        raise ValidationError(error_messages)

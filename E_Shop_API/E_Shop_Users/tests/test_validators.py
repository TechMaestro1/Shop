# python manage.py test E_Shop_API.E_Shop_Users.tests.test_validators
from datetime import datetime
from unittest import TestCase
from django.core.exceptions import ValidationError
from E_Shop_API.E_Shop_Users.tests.helpers.error_messages import ErrorMessages
from E_Shop_API.E_Shop_Users.validators import birthday_validator, validate_password


class BirthdayValidatorTest(TestCase):
    """ Testing Birthday Validator """

    # test variable
    correct_date = datetime.now().strftime('%Y-%m-%d')
    incorrect_date = datetime.now().strftime('%m-%y-%d')

    def test_correct_date_format(self):
        """ Checking the correct date format """
        self.assertIsNone(birthday_validator(datetime.strptime(self.correct_date, "%Y-%m-%d").date()))

    def test_incorrect_date_format(self):
        """ Checking the wrong date format """
        with self.assertRaises(ValueError):
            birthday_validator(datetime.strptime(self.incorrect_date, "%Y-%m-%d").date())

    def test_future_date(self):
        """ Checking the future date format """
        with self.assertRaises(ValidationError) as context:
            birthday_validator(datetime.strptime('2050-12-31', "%Y-%m-%d").date())
        self.assertIn(ErrorMessages.CANNOT_BE_FUTURE, context.exception.messages)

    def test_less_1970(self):
        """ Checking the date format less 1970-01-01 """
        with self.assertRaises(ValidationError) as context:
            birthday_validator(datetime.strptime('1920-01-01', "%Y-%m-%d").date())
        self.assertIn(ErrorMessages.YEAR_IS_NOT_VALID, context.exception.messages)


class PasswordValidatorTest(TestCase):
    """ Testing Password Validator """

    def test_short_password(self):
        """ Checking if the password is too short """
        with self.assertRaises(ValidationError) as context:
            validate_password('short')
        self.assertIn(ErrorMessages.MIN_8_CHARACTERS, context.exception.messages)

    def test_password_without_numbers(self):
        """ Checking if the password without numbers """
        with self.assertRaises(ValidationError) as context:
            validate_password('PasswordWithoutNumbers')
        self.assertIn(ErrorMessages.AT_LEAST_ONE_DIGIT, context.exception.messages)

    def test_password_without_capital_letters(self):
        """ Checking if the password without upper letters """
        with self.assertRaises(ValidationError) as context:
            validate_password('passwordwithoutcapitalletters')
        self.assertIn(ErrorMessages.UPPER_CASE_LETTER, context.exception.messages)

    def test_valid_password(self):
        """ Should not raise any exception for a valid password """
        try:
            validate_password('ValidPasswordWith1Capital')
        except ValidationError:
            self.fail("Invalid Password")

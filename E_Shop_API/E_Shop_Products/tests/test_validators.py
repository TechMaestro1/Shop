# python manage.py test E_Shop_API.E_Shop_Products.tests.test_validators
from django.test import TestCase
from django.core.exceptions import ValidationError
from E_Shop_API.E_Shop_Products.validators import validate_negative
from E_Shop_API.E_Shop_Users.tests.helpers.error_messages import ErrorMessages


class ValidatorsTestCase(TestCase):
    def test_positive_value_does_not_raise_error(self):
        """ Positive values should not raise a ValidationError when using validate_negative """
        try:
            validate_negative(10)
        except ValidationError as e:
            self.fail(f"Unexpected ValidationError raised: {e}")

    def test_zero_value_returns_false(self):
        """ Zero values should return False when using validate_negative """
        result = validate_negative(0)
        self.assertFalse(result)

    def test_negative_value_raises_error(self):
        """ Negative values should raise a ValidationError when using validate_negative """
        with self.assertRaises(ValidationError) as cm:
            validate_negative(-10)

        expected_error_message = [ErrorMessages.NEGATIVE_VALUE]
        self.assertEqual(cm.exception.messages, expected_error_message)

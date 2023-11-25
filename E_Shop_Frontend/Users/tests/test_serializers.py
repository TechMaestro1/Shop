# python manage.py test E_Shop_Frontend.Users.tests.test_serializers
from django.test import TestCase
from E_Shop_Frontend.Users.serializers import ClientsCreationForm
from E_Shop_API.E_Shop_Users.tests.helpers.error_messages import ErrorMessages


class ClientsCreationFormTests(TestCase):
    def setUp(self):
        self.valid_data = {
            'username': 'john_doe',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'birth_date': '1990-01-01',
            'password1': 'StrongP@ssword123',
            'password2': 'StrongP@ssword123',
            'photo': None,
            'disabled': False,
        }

    def test_clients_creation_form_valid(self):
        """ Test a valid clients creation form """
        form = ClientsCreationForm(data=self.valid_data)
        self.assertTrue(form.is_valid())

    def test_clients_creation_form_invalid_email(self):
        """ Test an invalid email in clients creation form """
        form_data = self.valid_data.copy()
        form_data['email'] = 'invalid_email'
        form = ClientsCreationForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_clients_creation_form_password_invalid(self):
        """ Test invalid password in clients creation form """
        form_data = self.valid_data.copy()
        form_data['password1'] = 'WeakPassword'
        form_data['password2'] = 'WeakPassword'
        form = ClientsCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        password_errors = form.errors['password1']

        # Check for the presence of the correct error message
        self.assertIn(ErrorMessages.AT_LEAST_ONE_DIGIT, password_errors)

    def test_clients_creation_form_password_mismatch(self):
        """ Test password mismatch in clients creation form """
        form_data = self.valid_data.copy()
        form_data['password2'] = 'DifferentPassword'
        form = ClientsCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)
        self.assertEqual(form.errors['password2'], ["The two password fields didn’t match."])
# python manage.py test E_Shop_Frontend.Users.tests.test_forms
from django.test import TestCase
from E_Shop_API.E_Shop_Users.tests.helpers.test_helpers import create_basic_user
from E_Shop_Frontend.Users.forms import UserRegistrationForm, UserEditForm


class UserFormTests(TestCase):
    def test_user_registration_form_valid(self):
        """ Test a valid user registration form """
        form_data = {
            'username': 'User',
            'first_name': 'User',
            'last_name': 'User',
            'email': 'user@gmail.com',
            'birth_date': '1990-01-01',
            'password1': 'UserPass123',
            'password2': 'UserPass123'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_user_registration_form_invalid(self):
        """ Test an invalid user registration form """
        form_data = {
            'first_name': 'User',
            'last_name': 'User',
            'email': 'user@gmail.com',
            'birth_date': '1990-01-01',
            'password1': 'WeakPassword',
            'password2': 'WeakPassword'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_user_edit_form_valid(self):
        """ Test a valid user edit form """
        user = create_basic_user()
        form_data = {
            'username': 'User',
            'first_name': 'User',
            'last_name': 'User',
            'email': 'user@gmail.com',
            'birth_date': '1990-01-01',
            'current_password': 'UserPass123',
        }
        form = UserEditForm(data=form_data, instance=user)
        self.assertTrue(form.is_valid())

    def test_user_edit_form_invalid(self):
        """ Test an invalid user edit form """
        user = create_basic_user()
        form_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'invalid_email',
            'birth_date': '1990-01-01',
        }
        form = UserEditForm(data=form_data, instance=user)
        self.assertFalse(form.is_valid())

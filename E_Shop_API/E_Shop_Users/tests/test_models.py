# python manage.py test E_Shop_API.E_Shop_Users.tests.test_models
from django.test import TestCase
from E_Shop_API.E_Shop_Users.models import Clients
from E_Shop_API.E_Shop_Users.tests.settings_module import django
from E_Shop_API.E_Shop_Users.tests.helpers.test_helpers import create_basic_user, create_admin_user

django.setup()  # DJANGO_SETTINGS_MODULE


class ClientsModelTest(TestCase):
    """ Test cases for the Clients model """

    def tearDown(self):
        Clients.objects.all().delete()

    def test_create_user(self):
        """ Create a new user and check if all fields are correct """
        user = create_basic_user()
        self.assertEqual(user.username, "User")
        self.assertEqual(user.first_name, "User")
        self.assertEqual(user.last_name, "User")
        self.assertEqual(user.email, "user@gmail.com")
        self.assertTrue(user.check_password("UserPass123"))
        self.assertIsNone(user.birth_date)
        self.assertFalse(user.disabled)

    def test_create_admin(self):
        """ Test creating a new superuser """
        admin = create_admin_user()
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)

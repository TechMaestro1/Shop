# python manage.py test E_Shop_API.E_Shop_Users.tests.test_serializers
from django.test import TestCase
from django.contrib.sites.models import Site
from django.contrib.auth.hashers import check_password

from rest_framework.test import APITestCase
from allauth.socialaccount.models import SocialApp

from E_Shop_API.E_Shop_Users import serializers
from E_Shop_API.E_Shop_Users.tests.helpers.test_helpers import create_basic_user
from E_Shop_API.E_Shop_Users.tests.settings_module import django

django.setup()


class UserDetailSerializerTest(TestCase):
    """ Test UserDetailSerializer """

    def setUp(self):
        """ Set up a user object for use in tests """
        self.user = create_basic_user()

    def test_serializer_returns_correct_values(self):
        """ Test that UserDetailSerializer returns the correct values """
        serializer = serializers.UserDetailSerializer(instance=self.user)
        expected_data = {
            'id': self.user.id,
            'username': 'User',
            'first_name': 'User',
            'last_name': 'User',
            'email': 'user@gmail.com',
            'birth_date': None,
            'photo': None,
            'disabled': False,
            'created_at': serializer.data.get('created_at'),
            'updated_at': serializer.data.get('updated_at')
        }
        expected_data['id'] = str(expected_data['id'])
        self.assertEqual(serializer.data, expected_data)


class MyUserSerializerTestCase(TestCase):
    """ Test MyUserSerializer """

    def setUp(self):
        """ Set up a client object for use in tests """
        self.client = create_basic_user()

    def test_missing_password(self):
        """ Test that an empty password field is not accepted """
        data = {
            'username': 'test',
            'first_name': 'Test',
            'last_name': 'Test',
            'email': 'test@test.com',
            'birth_date': '1990-01-01',
            'password': '',
        }
        serializer = serializers.MyUserSerializer(instance=self.client, data=data, partial=True)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)

    def test_valid_data(self):
        """ Test that serializer accepts valid data and saves to database """
        data = {
            'username': 'test',
            'first_name': 'Test',
            'last_name': 'Test',
            'email': 'test@test.com',
            'password': 'newtestpassworD1',
            'birth_date': '1990-01-01',
        }
        serializer = serializers.MyUserSerializer(instance=self.client, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertTrue(check_password(data['password'], user.password))


class SiteSerializerTestCase(TestCase):
    """ Test SiteSerializer """

    def test_site_serializer(self):
        """ Test that SiteSerializer correctly updates a site instance """
        site = Site.objects.create(domain='test_site.com', name='Test Site')
        data = {'domain': 'new_test_site.com', 'name': 'New Test Site'}
        serializer = serializers.SiteSerializer(instance=site, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_site = serializer.save()
        self.assertEqual(updated_site.domain, data['domain'])
        self.assertEqual(updated_site.name, data['name'])


class SocialAppSerializerTestCase(APITestCase):
    """ Test case for the SocialAppSerializer class """

    def setUp(self):
        """ Set up a SocialApp instance for testing """
        self.social_app = SocialApp.objects.create(
            provider='facebook',
            name='Facebook',
            client_id='client_id',
            secret='secret',
            key='key',
        )

    def test_valid_data(self):
        """ Test creating a new social app with valid data """
        data = {
            'provider': 'google',
            'name': 'Google',
            'client_id': 'client_id',
            'secret': 'secret',
            'key': 'key',
        }
        serializer = serializers.SocialAppSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        social_app = serializer.save()
        self.assertEqual(social_app.provider, data['provider'])
        self.assertEqual(social_app.name, data['name'])
        self.assertEqual(social_app.client_id, data['client_id'])
        self.assertEqual(social_app.secret, data['secret'])
        self.assertEqual(social_app.key, data['key'])

    def test_invalid_data(self):
        """ Test that invalid data is not accepted by the serializer """
        data = {"name": "", "provider": ""}
        serializer = serializers.SocialAppSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(len(serializer.errors), 3)

    def test_update_social_app_details(self):
        """ Test updating social app details """
        new_provider = 'google'
        new_name = 'Google'
        data = {'provider': new_provider, 'name': new_name}
        serializer = serializers.SocialAppSerializer(instance=self.social_app, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        social_app = serializer.save()
        self.assertEqual(social_app.provider, new_provider)
        self.assertEqual(social_app.name, new_name)

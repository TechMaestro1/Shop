# python manage.py test E_Shop_API.E_Shop_Users.tests.test_views
import json
from rest_framework import status
from rest_framework.test import APITestCase

from django.contrib.sites.models import Site
from django.urls import reverse, NoReverseMatch
from allauth.socialaccount.models import SocialApp

from E_Shop_API.E_Shop_Users.models import Clients
from E_Shop_API.E_Shop_Users.serializers import SiteSerializer
from E_Shop_API.E_Shop_Users.tests.settings_module import django
from E_Shop_API.E_Shop_Users.tests.helpers.test_helpers import create_admin_user, create_basic_user

django.setup()  # DJANGO_SETTINGS_MODULE


def get_user_data():
    """ TESTS DATA """
    return {
        'username': 'Test',
        'email': 'newemail@test.com',
        'first_name': 'New_test_name',
        'last_name': 'New_test_last_name',
        'password': 'Test_password1'
    }


class UserDetailViewTestCase(APITestCase):
    """ TESTCASE User Detail View get/put/patch/delete """

    def setUp(self):
        """ TEST Field """
        self.user = create_basic_user()
        try:
            self.url = reverse('user_detail_view', kwargs={'pk': self.user.pk})
        except NoReverseMatch:
            self.url = None
            raise Exception('URL not found, user_detail_view')

    def assert_user_data_equal(self, data):
        """ TEST for update Fields """
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, data['username'])
        self.assertEqual(self.user.email, data['email'])
        self.assertEqual(self.user.first_name, data['first_name'])
        self.assertEqual(self.user.last_name, data['last_name'])
        self.assertTrue(self.user.check_password(data['password']))


class MyUserViewTestCase(APITestCase):
    """ TESTCASE CRUD my user 'auth/users/me' """

    def setUp(self):
        """ TEST Field """
        self.user = create_basic_user()
        self.client.force_login(self.user)

    def test_get_my_user_info(self):
        """ TEST GET MY_USER information """
        url = reverse('my_user_view')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response_content = response.content.decode('utf-8')
        response_data = json.loads(response_content)
        self.assertEqual(response_data['email'], self.user.email)
        self.assertEqual(response_data['first_name'], self.user.first_name)
        self.assertEqual(response_data['last_name'], self.user.last_name)

    def check_user_data(self, user, data, response):
        """ TEST UPDATE FIELDS """
        self.assertEqual(user.username, data["username"])
        self.assertEqual(user.first_name, data["first_name"])
        self.assertEqual(user.last_name, data["last_name"])
        self.assertEqual(user.email, data["email"])
        self.assertNotEqual(user.password, data["password"])
        self.assertTrue(user.check_password(data["password"]))

        response_data = json.loads(response.content)
        self.assertEqual(response_data["id"], str(self.user.pk))
        self.assertEqual(response_data["username"], data["username"])
        self.assertEqual(response_data["first_name"], data["first_name"])
        self.assertEqual(response_data["last_name"], data["last_name"])
        self.assertEqual(response_data["email"], data["email"])
        self.assertEqual(response_data["birth_date"], None)
        self.assertEqual(response_data["photo"], None)
        self.assertEqual(response_data["disabled"], False)
        self.assertIsNotNone(response_data["created_at"])
        self.assertIsNotNone(response_data["updated_at"])

    def test_put_my_user_info(self):
        """ TEST PUT My_User fields """
        self.client.force_authenticate(user=self.user)
        data = get_user_data()
        response = self.client.put(reverse("my_user_view"), data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that user details have been updated
        user = Clients.objects.get(pk=self.user.pk)
        self.check_user_data(user, data, response)

    def test_patch_my_user_info(self):
        """ TEST PATCH My_User fields """
        self.client.force_authenticate(user=self.user)
        data = get_user_data()
        response = self.client.patch(reverse("my_user_view"), data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that user details have been updated
        user = Clients.objects.get(pk=self.user.pk)
        self.check_user_data(user, data, response)


class SiteViewTestCase(APITestCase):
    """ TESTCASE Google SocialApp """

    def setUp(self):
        """ Create an admin user and authenticate as an admin for test setup """
        Site.objects.filter(domain='example.com').delete()
        self.site = Site.objects.create(name='example.com', domain='example.com')
        self.admin_user = create_admin_user()

    def test_update_site(self):
        """ Test updating a site """
        data = {'name': 'updated-example.com', 'domain': 'updated-example.com'}
        url = reverse('site_detail', kwargs={'pk': self.site.pk})
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.put(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.site.refresh_from_db()
        self.assertEqual(self.site.name, data['name'])
        self.assertEqual(self.site.domain, data['domain'])
        self.assertEqual(response.data, SiteSerializer(self.site).data)


class SelectSocialApplicationViewTestCase(APITestCase):
    """ TESTCASE Google Provider """

    def setUp(self):
        """ Create an admin user and authenticate as an admin for test setup """
        self.admin_user = create_admin_user()
        self.client.force_authenticate(user=self.admin_user)

    def test_get_social_app(self):
        """ Test retrieving a social app by ID """
        social_app = SocialApp.objects.create(name='Test App', client_id='abc123', provider='google')
        url = reverse('select_social_application', kwargs={'pk': social_app.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_social_app(self):
        """ Test creating a social app with invalid data """
        data = {'name': 'Test App', 'client_id': 'abc123', 'client_secret': 'def456'}
        social_app = SocialApp.objects.create(provider='google')
        url = reverse('select_social_application', kwargs={'pk': social_app.pk})
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

from django.test import TestCase
from django.urls import reverse

from E_Shop_API.E_Shop_Users.tests.helpers.test_helpers import create_basic_user


class UsersURLsAndViewsTest(TestCase):
    def setUp(self):
        self.user = create_basic_user()

    def test_registration_view(self):
        """ Test the registration view """
        response = self.client.get(reverse('registration'))
        self.assertEqual(response.status_code, 200)

    def test_forgot_password_view(self):
        """ Test the forgot_password view """
        response = self.client.get(reverse('forgot_password'))
        self.assertEqual(response.status_code, 200)

    def test_password_reset_view(self):
        """ Test the password_reset view """
        response = self.client.get(reverse('password_reset'))
        self.assertEqual(response.status_code, 302)

    def test_resend_confirmation_view(self):
        """ Test the resend_confirmation view """
        response = self.client.get(reverse('resend_confirmation'))
        self.assertEqual(response.status_code, 405)

    def test_confirm_account_view(self):
        """ Test the confirm_account view with valid UID and token """
        uid = self.user.pk
        token = 'valid-token'  # Replace with a valid token
        url = reverse('confirm_account', args=[uid, token])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Redirects to the home page

    def test_login_view(self):
        """ Test the login view """
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_logout_view(self):
        """ Test the logout view """
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)  # Redirects to the home page

    def test_user_profile_view(self):
        """ Log in the user before testing the user_profile view """
        self.client.login(username='user@gmail.com', password='UserPass123')

        # Test the user_profile view
        response = self.client.get(reverse('user_profile'))
        self.assertEqual(response.status_code, 200)

    def test_delete_photo_view(self):
        """ Log in the user before testing the delete_photo view """
        self.client.login(username='user@gmail.com', password='UserPass123')

        # Test the delete_photo view
        response = self.client.post(reverse('delete_photo'))
        self.assertEqual(response.status_code, 302)  # Redirects to the user_profile page

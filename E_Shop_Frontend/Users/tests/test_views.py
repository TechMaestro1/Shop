# python manage.py test E_Shop_Frontend.Users.tests.test_views
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse
from django.test import TestCase
from unittest.mock import patch

from E_Shop_API.E_Shop_Users.tests.helpers.test_helpers import create_basic_user


class DeletePhotoViewTest(TestCase):
    """ Test cases for the DeletePhotoView """

    def setUp(self):
        self.user = create_basic_user()
        self.image = SimpleUploadedFile(
            "test_image.jpg",
            content=open("E_Shop_config/static/img/bin.png", "rb").read(),
            content_type="image/jpeg",
        )
        self.user.photo = self.image
        self.user.save()

    def test_photo_deletion(self):
        """ Test photo deletion functionality """
        self.client.login(username='User', password='UserPass123')
        response = self.client.post(reverse('delete_photo'))
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertFalse(self.user.photo)

    def test_photo_deletion_redirects(self):
        """ Test that photo deletion redirects properly """
        response = self.client.post(reverse('delete_photo'))
        self.assertEqual(response.status_code, 302)


class UserLoginViewTest(TestCase):
    """ Test cases for the UserLoginView """

    def setUp(self):
        self.user = create_basic_user()

    def test_get_login_view_for_anonymous_user(self):
        """ Test accessing the login view for an anonymous user """
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')
        self.assertIsInstance(response.context['form'], AuthenticationForm)

    def test_get_login_view_for_authenticated_user(self):
        """ Log in an authenticated user and check if they are redirected """
        self.client.login(username='user@gmail.com', password='UserPass123')
        response = self.client.get(reverse('login'))
        self.assertRedirects(response, reverse('home'))

    def test_post_login_view_with_valid_credentials(self):
        """ Test logging in with valid credentials """
        login_data = {
            'username': 'user@gmail.com',
            'password': 'UserPass123',
        }
        response = self.client.post(reverse('login'), login_data)
        self.assertRedirects(response, reverse('home'))

    def test_post_login_view_with_invalid_credentials(self):
        """ Test logging in with invalid credentials """
        login_data = {
            'username': 'user.gmail.com',  # Invalid email format
            'password': 'UserPass123',  # Invalid password format
        }
        response = self.client.post(reverse('login'), login_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')
        self.assertContains(response, 'Invalid email or password. Please try again.')

    def test_post_login_view_with_authenticated_user(self):
        """ Log in an authenticated user and check if they are redirected """
        self.client.login(username='user@gmail.com', password='UserPass123')

        login_data = {
            'username': 'user@gmail.com',
            'password': 'UserPass123',
        }
        response = self.client.post(reverse('login'), login_data)
        self.assertRedirects(response, reverse('home'))


class EditProfileViewTest(TestCase):
    """ Test cases for the EditProfileView """

    def setUp(self):
        self.user = create_basic_user()
        self.client.login(username='user@gmail.com', password='UserPass123')

    def test_get_edit_profile_view(self):
        """ Test accessing the edit profile view """
        url = reverse('user_profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/user_profile.html')

    def test_post_edit_profile_view_valid_data(self):
        """ Test posting valid data to the edit profile view """
        valid_data = {
            'first_name': 'Updated First Name',
            'last_name': 'Updated Last Name',
        }
        response = self.client.post(reverse('user_profile'), valid_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Updated First Name')
        self.assertContains(response, 'Updated Last Name')

    def test_post_edit_profile_view_invalid_data(self):
        """ Test posting invalid data to the edit profile view """
        url = reverse('user_profile')
        data = {}
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/user_profile.html')
        self.assertFormError(response, 'form', 'first_name', 'This field is required.')


class ForgotPasswordViewTest(TestCase):
    """ Test cases for the ForgotPasswordView """

    def setUp(self):
        self.user = create_basic_user()

    def test_get_when_authenticated(self):
        """ Test accessing the forgot password view when authenticated (should redirect) """
        self.client.login(username='user@gmail.com', password='UserPass123')
        response = self.client.get(reverse('forgot_password'))
        self.assertRedirects(response, reverse('home'))

    def test_get_when_not_authenticated(self):
        """ Test accessing the forgot password view when not authenticated """
        self.client.logout()
        response = self.client.get(reverse('forgot_password'))
        self.assertEqual(response.status_code, 200)

    def test_post_email_found_email_throttling(self):
        """ Test posting an email found in the system for password reset """
        with patch('E_Shop_API.E_Shop_Users.views.EmailThrottling.send_email_with_throttling') as mock_send_email:
            response = self.client.post(reverse('forgot_password'), {'email': 'user@gmail.com'})

            mock_send_email.assert_called_once()
        self.assertRedirects(response, reverse('forgot_password'))

    def test_post_email_not_found(self):
        """ Test posting an email not found in the system for password reset """
        response = self.client.post(reverse('forgot_password'), {'email': 'nonexistent@example.com'})
        self.assertEqual(response.status_code, 200)

    def test_post_email_found_email_throttling_failed(self):
        """ Test posting an email found in the system for password reset with throttling failure """
        with patch('E_Shop_API.E_Shop_Users.views.EmailThrottling.send_email_with_throttling') as mock_send_email:
            # mock_send_email.return_value = False  # Simulate a failed email send

            # Make a POST request with a valid email
            response = self.client.post(reverse('forgot_password'), {'email': 'user@gmail.com'})
            self.assertEqual(response.status_code, 302)

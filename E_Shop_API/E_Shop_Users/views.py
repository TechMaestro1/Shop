from datetime import timedelta
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone

from rest_framework import permissions, status
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from allauth.socialaccount.models import SocialApp
from E_Shop_API.E_Shop_Users import serializers
from E_Shop_API.E_Shop_Users.models import Clients


class EmailThrottling:
    """ Limits on sending email letters """

    @staticmethod
    def send_email_with_throttling(email_address, subject, html_message, cache_key, timeout=60):
        last_sent_time = cache.get(cache_key)

        if last_sent_time:
            time_elapsed = timezone.now() - last_sent_time
            if time_elapsed < timedelta(minutes=1):
                return False

        send_mail(subject, '', settings.EMAIL_HOST_USER, [email_address], html_message=html_message)
        cache.set(cache_key, timezone.now(), timeout=timeout)
        return True


class MyUserView(APIView):
    """ Information about my user 'auth/users/me' """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """ GET Method user 'auth/users/me/' """
        get_user = self.request.user
        user = Clients.objects.get(pk=get_user.pk)
        serializer = serializers.UserDetailSerializer(user)
        return JsonResponse(serializer.data)

    def put(self, request):
        """ PUT Method user 'auth/users/me/' """
        get_user = self.request.user
        user = Clients.objects.get(pk=get_user.pk)
        serializer = serializers.MyUserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)

    def patch(self, request):
        """ PATCH Method user 'auth/users/me/' """
        get_user = self.request.user
        user = Clients.objects.get(pk=get_user.pk)
        serializer = serializers.MyUserSerializer(get_user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

    @classmethod
    def delete(cls, request):
        """ HIDE Method user 'auth/users/me/' """
        user = request.user
        if user.is_active:
            user.is_active = False
            user.save()
            return Response({'message': 'User deactivated'}, status=status.HTTP_200_OK)
        return Response({'message': 'User is already deactivated'}, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(APIView):
    """ User Detail View get/put/patch/delete """
    permission_classes = [permissions.IsAdminUser, ]

    @staticmethod
    def get(request, pk):
        """ GET Method user/<int:pk>/ """
        user = Clients.objects.get(pk=pk)
        serializer = serializers.UserDetailSerializer(user)
        return Response(serializer.data)

    @staticmethod
    def put(request, pk):
        """ PUT Method user/<int:pk>/ """
        user = Clients.objects.get(pk=pk)
        serializer = serializers.MyUserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)

    @staticmethod
    def patch(request, pk):
        """ PATCH Method user/<int:pk>/ """
        user = Clients.objects.get(pk=pk)
        serializer = serializers.MyUserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)

    @staticmethod
    def delete(request, pk):
        """ DELETE/HIDE Method user/<int:pk>/ """
        user = Clients.objects.get(pk=pk)
        if user.is_active:
            user.is_active = False
            user.save()
            return Response({'message': 'User deactivated'}, status=status.HTTP_200_OK)
        return Response({'message': 'User is already deactivate'}, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def post(request, pk):
        """ Activate a disabled user """
        user = Clients.objects.get(pk=pk)
        if not user.is_active:
            user.is_active = True
            user.save()
            return Response({'message': 'User activated'}, status=status.HTTP_200_OK)
        return Response({'message': 'User is already active'}, status=status.HTTP_400_BAD_REQUEST)


class SendActivationView(APIView):
    """ Send activation link on mail """

    @staticmethod
    def post(request):
        serializer = serializers.ActivationRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']

            client = get_user_model()
            if not client.objects.filter(email=email).exists():
                return Response({'error': 'Email not found in the database'}, status=status.HTTP_404_NOT_FOUND)
            activation_link = request.build_absolute_uri(reverse('activate_user') + f'?email={email}')
            cache_key = f"activation_email_{email}"
            if not EmailThrottling.send_email_with_throttling(
                    email,
                    'Activation Letter',
                    render_to_string('email_templates/activation_email.html', {'activation_link': activation_link}),
                    cache_key
            ):
                return Response({'error': 'Activation email can only be sent once per minute.'},
                                status=status.HTTP_429_TOO_MANY_REQUESTS)

            return Response({'message': 'Activation link sent to your email'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ActivateUserView(APIView):
    """ Function which activate user """

    @staticmethod
    def get(request):
        get_email = request.GET.get('email')
        try:
            user = Clients.objects.get(email=get_email)
            user.is_active = True
            user.save()
            return redirect('home')
        except Clients.DoesNotExist:
            return redirect('404')


class ForgotPasswordAPI(APIView):
    @staticmethod
    def post(request, *args, **kwargs):
        email = request.data.get('email')
        try:
            user = Clients.objects.get(email=email)
        except Clients.DoesNotExist:
            return Response({'error': 'User with this email does not exist'}, status=status.HTTP_404_NOT_FOUND)

        reset_link = request.build_absolute_uri(
            f"/reset_password/?user={user.id}")

        cache_key = f"password_reset_email_{email}"
        if not EmailThrottling.send_email_with_throttling(
                email,
                'Password Reset Request',
                render_to_string('email_templates/reset_message.html', {'reset_link': reset_link}),
                cache_key
        ):
            return Response({'error': 'Password reset email can only be sent once per minute.'},
                            status=status.HTTP_429_TOO_MANY_REQUESTS)

        return Response({'message': 'Password reset link has been sent to your email'}, status=status.HTTP_200_OK)


# GOOGLE OAUTH PROVIDER
class SiteView(RetrieveUpdateAPIView):
    """ Domain site """
    permission_classes = [permissions.IsAdminUser, ]

    queryset = Site.objects.all()
    serializer_class = serializers.SiteSerializer
    lookup_field = 'pk'

    def update(self, request, *args, **kwargs):
        """ Update site """
        site = Site.objects.get(pk=kwargs['pk'])
        site.domain = request.data.get('domain')
        site.name = request.data.get('name')
        site.save()
        return Response(serializers.SiteSerializer(site).data)


class SelectSocialApplicationView(APIView):
    """ GOOGLE OAUTH PROVIDER """
    permission_classes = [permissions.IsAdminUser, ]

    @staticmethod
    def get(request, pk):
        """ Retrieve a social app by ID """
        try:
            social_app = SocialApp.objects.get(pk=pk)
            serializer = serializers.SocialAppSerializer(social_app)
            return Response(serializer.data)
        except SocialApp.DoesNotExist:
            return Response({"error": "Social application with id {} does not exist".format(pk)})

    @staticmethod
    def post(request, pk):
        """ Create a social app with provided data """
        serializer = serializers.SocialAppSerializer(data=request.data)
        if serializer.is_valid():
            social_app = serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

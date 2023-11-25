from datetime import datetime, timedelta
from functools import wraps

from django.contrib import messages
from django.contrib.auth import get_user_model, login, authenticate
from django.contrib.auth.hashers import make_password
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.views import View
from django.views.generic import TemplateView

from E_Shop_API.E_Shop_Users.models import Clients
from E_Shop_API.E_Shop_Users.validators import validate_password
from E_Shop_API.E_Shop_Users.views import EmailThrottling
from E_Shop_config.tasks import send_confirm_email
from E_Shop_Frontend.Users.forms import UserEditForm, UserRegistrationForm


class ThrottleActivationEmail:
    def __init__(self, timeout=60):
        self.timeout = timeout

    def __call__(self, view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated:
                email = request.user.email
                cache_key = f"activation_email_{email}"
                last_sent_time = cache.get(cache_key)
                if last_sent_time and (datetime.now() - last_sent_time) < timedelta(seconds=self.timeout):
                    messages.warning(request, 'Email can only be sent once per minute')
                    return redirect('home')
                cache.set(cache_key, datetime.now(), timeout=self.timeout)
            return view_func(request, *args, **kwargs)

        return _wrapped_view


@method_decorator(ThrottleActivationEmail(timeout=60), name='dispatch')
class RegistrationView(View):
    """ Registration new user /registration/ """

    form_class = UserRegistrationForm
    template_name = 'registration/registration.html'
    success_url = reverse_lazy('home')

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')

        user_is_active = request.session.get('user_is_active', False)
        form = self.form_class()

        if user_is_active:
            form = None

        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()

            # Log in the new user
            user = authenticate(request, email=form.cleaned_data.get('email'),
                                password=form.cleaned_data.get('password1'))
            if user is not None:
                login(request, user)  # Log in the user

            # Call the resend_confirmation view to send the activation email

            resend_confirmation_view = ResendConfirmationView()

            resend_confirmation_view.post(request)

            return redirect(self.success_url)
        return render(request, self.template_name, {'form': form})


class UserLoginView(View):
    """ Login as user /login/ """
    template_name = 'registration/login.html'
    form_class = AuthenticationForm

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
        return render(request, self.template_name, {'form': form})


class ForgotPassword(TemplateView):
    """ Send letter Forgot Password """
    template_name = 'registration/forgot_password.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        email = request.POST.get('email')
        try:
            user = Clients.objects.get(email=email)
        except Clients.DoesNotExist:
            return render(request, self.template_name, {'form_errors': True})

        reset_link = request.build_absolute_uri(
            f"/reset_password/?user={user.id}")

        cache_key = f"password_reset_email_{email}"
        if not EmailThrottling.send_email_with_throttling(
                email,
                'Password Reset Request',
                render_to_string('email_templates/reset_message.html', {'reset_link': reset_link}),
                cache_key
        ):
            messages.warning(request, "Password reset email can only be sent once per minute")
            return redirect(request.path)

        messages.success(request, 'Password reset link has been sent to your email')
        return redirect(request.path)


class PasswordReset(View):
    """ Handles the password reset process """
    template_name = 'registration/reset_password.html'

    def get(self, request, *args, **kwargs):
        # Check if the user exists with the provided user ID (from the reset link)
        user_id = request.GET.get('user')
        try:
            user = Clients.objects.get(pk=user_id)
            request.session['reset_user_id'] = user_id
            return render(request, self.template_name)
        except Clients.DoesNotExist:
            return redirect('404')

    def post(self, request, *args, **kwargs):
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        form_errors = []

        if new_password != confirm_password:
            form_errors.append("Passwords do not match.")

        try:
            validate_password(new_password)
        except ValidationError as e:
            form_errors.extend(e.messages)

        if form_errors:
            return render(request, self.template_name, {'form_errors': form_errors})

        try:
            user_id = request.session.get('reset_user_id')
            user = Clients.objects.get(pk=user_id)
        except Clients.DoesNotExist:
            return redirect('404')

        user.password = make_password(new_password)  # Hash the new password before saving
        user.save()
        del request.session['reset_user_id']  # Clear the session variable after password reset
        return redirect('home')


@method_decorator(ThrottleActivationEmail(timeout=60), name='dispatch')
class ResendConfirmationView(View):
    """ Resend confirmation email /resend_confirmation/ """

    @staticmethod
    def post(request):
        if request.method == 'POST':
            email = request.user.email
            user = get_object_or_404(get_user_model(), email=email)
            if not user.is_confirmed:
                # Call the Celery task to send the activation email asynchronously
                send_confirm_email.apply_async(args=[user.id, get_current_site(request).domain])

                messages.success(request, 'Confirmation email sent. Please check your inbox')

        return redirect('home')


class ConfirmAccountView(View):
    """ Confirm user account /confirm_account/ """

    @staticmethod
    def get(request, uid, token):
        try:
            uid = force_str(urlsafe_base64_decode(uid))
            user = get_user_model().objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
            user = None

        if user and default_token_generator.check_token(user, token):
            user.is_active = True
            user.is_confirmed = True
            user.save()
        return redirect('home')


class EditProfileView(LoginRequiredMixin, View):
    """ Edit the user's profile """
    template_name = 'pages/user_profile.html'
    form_class = UserEditForm
    success_url = 'user_profile'
    login_url = 'login'

    def get(self, request):
        form = self.form_class(instance=request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            # Validate the current password
            new_password = form.cleaned_data.get('new_password')
            if new_password:
                request.user.set_password(new_password)

            # Save the rest of the form fields
            form.save()
            return redirect(self.success_url)
        else:
            messages.error(request, 'There was an error updating your profile.')
            return render(request, self.template_name, {'form': form})


class DeletePhotoView(LoginRequiredMixin, View):
    """ Delete the user's profile photo """

    @staticmethod
    def post(request):
        user = request.user
        user.photo.delete()
        user.save()
        return redirect('user_profile')

from E_Shop_API.E_Shop_Users.validators import validate_password
from E_Shop_API.E_Shop_Users.models import Clients

from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _


class UserRegistrationForm(UserCreationForm):
    """ Create a form for registering new users in the system """
    first_name = forms.CharField(max_length=64, required=True)
    last_name = forms.CharField(max_length=64, required=True)
    email = forms.EmailField(max_length=254, required=True)
    birth_date = forms.DateField(required=True)
    photo = forms.ImageField(required=False)
    disabled = forms.BooleanField(required=False, initial=False)
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'required': 'required'}), validators=[validate_password])
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'required': 'required'}))

    class Meta:
        model = Clients
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'birth_date', 'photo')

    def clean_email(self):
        """ Check if email is unique """
        email = self.cleaned_data.get('email')
        if Clients.objects.filter(email=email).exists():
            raise forms.ValidationError(_('This email address is already in use.'))
        return email


class UserEditForm(UserChangeForm):
    """ Update the form to edit existing users in the system """
    first_name = forms.CharField(max_length=64, required=True)
    last_name = forms.CharField(max_length=64, required=True)
    email = forms.EmailField(max_length=254, required=True)
    birth_date = forms.DateField(required=False)
    photo = forms.ImageField(required=False)
    disabled = forms.BooleanField(required=False)
    current_password = forms.CharField(widget=forms.PasswordInput(), required=False)
    new_password = forms.CharField(validators=[validate_password], widget=forms.PasswordInput(), required=False)

    class Meta:
        model = Clients
        fields = ('username', 'first_name', 'last_name', 'email', 'birth_date', 'photo', 'disabled')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password'].widget = forms.HiddenInput()

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Clients.objects.filter(email=email).exclude(id=self.instance.id).exists():
            raise forms.ValidationError('This email address is already in use.')
        return email

    def clean(self):
        """Checking the current password entered by the user, if not correct, an error is displayed """
        super().clean()
        current_password = self.cleaned_data.get('current_password')
        if current_password:
            if not self.instance.check_password(current_password):
                self.add_error('current_password', 'The current password is incorrect.')

        new_password = self.cleaned_data.get('new_password')
        if new_password:
            self.instance.set_password(new_password)
        return self.cleaned_data

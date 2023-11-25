from django import forms
from E_Shop_API.E_Shop_Users.models import Clients
from django.contrib.auth.forms import UserCreationForm
from E_Shop_API.E_Shop_Users.validators import validate_password


class ClientsCreationForm(UserCreationForm):
    """ Register field """
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput(), validators=[validate_password])
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput())

    class Meta:
        model = Clients
        fields = [
            'username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'birth_date', 'photo', 'disabled']

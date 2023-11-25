import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from E_Shop_API.E_Shop_Users.validators import validate_password, birthday_validator


class Clients(AbstractUser):
    """ Clients models/fields """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(verbose_name='Name', max_length=64, blank=True)
    last_name = models.CharField(verbose_name='Surname', max_length=64, blank=True)

    email = models.EmailField(verbose_name='Email', unique=True, max_length=64, blank=False)
    password = models.CharField(validators=[validate_password], verbose_name='Password', max_length=88, blank=False)

    birth_date = models.DateField(verbose_name='Birthday', validators=[birthday_validator], blank=True, null=True)
    photo = models.ImageField(verbose_name='Photo', max_length=255, upload_to='photos', null=True, blank=True)

    disabled = models.BooleanField(verbose_name='Disabled?', default=False, blank=True)
    is_confirmed = models.BooleanField(verbose_name='Email Confirmed', default=False, blank=False)

    created_at = models.DateTimeField(verbose_name='Created at', auto_now_add=True, blank=False)
    updated_at = models.DateTimeField(verbose_name='Updated at', auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'password', 'birth_date', 'disabled', 'photo']

    def __str__(self):
        """ String representation """
        return self.username

    class Meta:
        """ Representation in admin panel """
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def save(self, *args, **kwargs):
        self.clean_fields(exclude=["photo"])
        super().save(*args, **kwargs)

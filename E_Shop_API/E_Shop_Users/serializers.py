from .models import Clients
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password

from django.contrib.sites.models import Site        # google
from allauth.socialaccount.models import SocialApp  # google


# USER
class UserDetailSerializer(serializers.ModelSerializer):
    """Return fields in  GET user detail """
    id = serializers.CharField(read_only=True)

    class Meta:
        model = Clients
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'birth_date', 'photo', 'disabled',
                  'created_at', 'updated_at']


class MyUserSerializer(serializers.ModelSerializer):
    """Return fields in  PUT/PATCH user """
    password = serializers.CharField(validators=[validate_password])

    class Meta:
        model = Clients
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'password', 'birth_date', 'photo', 'disabled',
                  'created_at', 'updated_at']

    def update(self, instance, validated_data):
        """ HASH Password when you update it"""
        user = super().update(instance, validated_data)
        try:
            user.set_password(validated_data['password'])
            user.save()
        except KeyError:
            pass
        return user


class ActivationRequestSerializer(serializers.Serializer):
    """ Activation account """
    email = serializers.EmailField()


# GOOGLE
class SiteSerializer(serializers.ModelSerializer):
    """ Change your domain """

    class Meta:
        model = Site
        fields = ('id', 'domain', 'name')


class SocialAppSerializer(serializers.ModelSerializer):
    """ Add provider """

    class Meta:
        model = SocialApp
        fields = '__all__'

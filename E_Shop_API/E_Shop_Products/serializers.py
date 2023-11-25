from .models import Product
from rest_framework import serializers


class ProductSerializer(serializers.ModelSerializer):
    """ Serializer which CRUD Product  'products/', 'product/<int:pk>/' """

    class Meta:
        model = Product
        fields = '__all__'

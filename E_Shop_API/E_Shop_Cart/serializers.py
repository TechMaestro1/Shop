from E_Shop_API.E_Shop_Cart.models import CartProduct
from rest_framework import serializers


class CartProductSerializer(serializers.ModelSerializer):
    """ Serializer which return Products in cart """
    name = serializers.ReadOnlyField(source='product.name')
    quantity = serializers.IntegerField()
    price = serializers.ReadOnlyField(source='subtotal')

    class Meta:
        model = CartProduct
        fields = ['name', 'quantity', 'price']

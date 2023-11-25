import uuid
from django.db import models
from datetime import timedelta

from E_Shop_config.tasks import delete_cart
from E_Shop_API.E_Shop_Users.models import Clients
from E_Shop_API.E_Shop_Products.models import Product


class Cart(models.Model):
    """  Cart models/fields  """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(Clients, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_cart_owner(self):
        """ Returns the owner of the cart """
        if self.user:
            return self.user

    @property
    def total_price(self):
        """ Calculate the total price of all products in the cart """
        total = 0
        for item in self.cart.all():
            total += item.product.price * item.quantity
        return total

    def __str__(self):
        """ String representation """
        return str(self.id)

    #     celery
    def schedule_deletion(self):
        """ Schedule the deletion of the cart (celery)"""
        delete_cart.apply_async((str(self.id),), eta=self.created_at + timedelta(minutes=1))


class CartProduct(models.Model):
    """  Cart models/fields  Product in cart """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='products')
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cart")
    quantity = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """String representation"""
        return self.product.name

    class Meta:
        unique_together = ('cart', 'product')

    def subtotal(self):
        """ Calculate the subtotal price for the cart product """
        return self.product.price * self.quantity

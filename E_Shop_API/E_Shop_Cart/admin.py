from django.contrib import admin
from E_Shop_API.E_Shop_Cart import models


class ProductInline(admin.StackedInline):
    """ Display cart_product in cart """
    model = models.CartProduct
    extra = 1


@admin.register(models.Cart)
class CartAdmin(admin.ModelAdmin):
    """ Register Cart model in admin panel """

    save_on_top = True

    inlines = [ProductInline]
    list_display = ("user", "total_price", "created_at")
    list_display_links = ("user", "total_price", "created_at")

    def total_price(self, obj):
        """ Return the total price of all products in the cart """
        return '{:.1f}'.format(obj.total_price)

    total_price.admin_order_field = 'total_price'

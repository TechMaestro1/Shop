import stripe
import base64
import os
from django.conf import settings
from django.shortcuts import redirect, render, get_object_or_404
from django.views import View
from django.urls import reverse
from E_Shop_API.E_Shop_Cart.models import Cart, CartProduct
from E_Shop_API.E_Shop_Products.models import Product
from E_Shop_Frontend.Users.email_sender import EmailSender
from django.http import HttpResponseRedirect

# STRIPE KEY
stripe.api_key = settings.STRIPE_SECRET_KEY


class CartMixin:
    """ Mixin to get the cart based on user authentication """

    @staticmethod
    def get_cart(request):
        if request.user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user=request.user)
            cart.schedule_deletion()  # Schedule deletion for authenticated users (celery)
            return cart


class CartOperationMixin:
    """ Mixin to perform common cart operations """

    @staticmethod
    def clear_cart_and_deduct_products(cart_id):
        cart = Cart.objects.get(id=cart_id)
        cart_products = CartProduct.objects.filter(cart=cart)

        for cart_product in cart_products:
            product = cart_product.product
            product.count -= cart_product.quantity
            product.save()

        cart_products.delete()


class AddToCartView(View, CartMixin):
    """ Add a product to the cart """

    def get(self, request, product_id):
        if not request.user.is_authenticated:
            return redirect('login')  # Ред
        cart = self.get_cart(request)
        product = get_object_or_404(Product, id=product_id)

        quantity = int(request.POST.get('quantity', 1))
        if quantity > product.count:
            quantity = product.count

        cart_product, created = CartProduct.objects.get_or_create(cart=cart, product=product)
        cart_product.quantity += quantity
        cart_product.save()

        return redirect('cart_detail')


class UpdateCartView(View, CartMixin):
    """ Update the cart """

    def post(self, request, product_id):
        cart = self.get_cart(request)
        product = get_object_or_404(Product, id=product_id)
        cart_product, created = CartProduct.objects.get_or_create(cart=cart, product=product)

        if request.method == 'POST':
            action = request.POST.get('action')

            if action == 'add':
                cart_product.quantity += 1
            elif action == 'remove':
                cart_product.quantity -= 1
            elif action == 'update':
                quantity = int(request.POST.get('quantity'))
                cart_product.quantity = quantity

            cart_product.save()

        return redirect('cart_detail')


class RemoveCartView(View, CartMixin):
    """ Remove a product from the cart """

    def get(self, request, product_id):
        cart = self.get_cart(request)
        product = get_object_or_404(Product, pk=product_id)
        cart_product = CartProduct.objects.get(cart=cart, product=product)
        cart_product.delete()
        return redirect('cart_detail')

    def post(self, request, product_id):
        return self.get(request, product_id)


class EmptyCartView(View, CartMixin):
    """ Remove all products from the cart """

    def get(self, request):
        cart = self.get_cart(request)
        cart_products = CartProduct.objects.filter(cart=cart)
        cart_products.delete()
        return redirect('cart_detail')


class CartDetailView(View, CartMixin):
    """ Display the cart contents """

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('login')  #
        cart = self.get_cart(request)
        cart_products = CartProduct.objects.filter(cart=cart).order_by('-created_at')

        for cart_product in cart_products:
            if cart_product.product.count == 0 or cart_product.quantity > cart_product.product.count:
                cart_product.delete()

        return render(request, 'pages/cart_detail.html', {'cart': cart, 'cart_products': cart_products})


class PaymentCartView(View, CartMixin):
    """ Processing the cart payment """

    def post(self, request):
        cart = self.get_cart(request)

        cart_products = CartProduct.objects.filter(cart=cart)
        line_items = []
        for cart_product in cart_products:
            product = cart_product.product
            if product.count < cart_product.quantity:
                error_message = "Check your cart, the quantity of the product is more than the available amount"
                return HttpResponseRedirect(reverse('404') + f'?error_message={error_message}')

            line_item = {
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': product.name,
                        'description': product.description,
                    },
                    'unit_amount': int(product.price * 100),
                },
                'quantity': cart_product.quantity,
            }
            line_items.append(line_item)

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=request.build_absolute_uri(reverse('payment_success')),
            cancel_url=request.build_absolute_uri(reverse('404')),
            metadata={
                'cart_id': str(cart.id)
            }
        )

        request.session['checkout_session_id'] = checkout_session.id
        request.session['cart_id'] = str(cart.id)
        request.session.modified = True

        return redirect(checkout_session.url)


class PaymentSuccessView(View, CartOperationMixin):
    """Successful payment cart"""

    def get(self, request):
        if 'checkout_session_id' in request.session and 'cart_id' in request.session:
            cart_id = request.session['cart_id']
            user_email = request.user.email
            user = request.user

            cart = Cart.objects.get(id=cart_id)
            total_price = cart.total_price
            cart_products = CartProduct.objects.filter(cart_id=cart_id)

            products = []
            for cart_product in cart_products:
                product = cart_product.product
                first_photo = product.photos.first()
                image_path = first_photo.image.path if first_photo else None

                products.append({
                    'id': product.id,
                    'name': product.name,
                    'description': product.description,
                    'count': cart_product.quantity,
                    'price': product.price * cart_product.quantity,
                    'image_path': image_path,
                })

            email_context = {
                'user': user,
                'email': user_email,
                'total_price': total_price,
                'products': products,
            }

            for product in products:
                image_path = product['image_path']
                if image_path:
                    image_full_path = os.path.join(settings.MEDIA_ROOT, image_path)
                    with open(image_full_path, 'rb') as f:
                        image_data = f.read()
                        image_base64 = base64.b64encode(image_data).decode()
                        product['image_base64'] = image_base64
                else:
                    product['image_base64'] = None

            EmailSender.send_inline_photo_email(user_email, email_context)

            self.clear_cart_and_deduct_products(cart_id)
            del request.session['checkout_session_id']
            del request.session['cart_id']
            request.session.modified = True

            return render(request, "pages/payment_success.html")
        else:
            return redirect(reverse('404'))

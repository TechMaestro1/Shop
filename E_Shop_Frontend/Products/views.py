from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator
from django.contrib import messages
from django.conf import settings
from django.urls import reverse
from django.db.models import Q

import base64
import random
import stripe

from django.views import View
from django.views.generic import TemplateView

from E_Shop_API.E_Shop_Cart.models import Cart, CartProduct
from E_Shop_API.E_Shop_Products.models import Product
from E_Shop_Frontend.Cart.views import CartMixin
from django.views.decorators.csrf import csrf_exempt
from E_Shop_Frontend.Users.email_sender import EmailSender

# STRIPE KEY
stripe.api_key = settings.STRIPE_SECRET_KEY


class BaseProductView(View):
    """Base function for other views"""

    @staticmethod
    def get_cart(request):
        """Get the cart based on user authentication or session"""
        if request.user.is_authenticated:
            cart_queryset = Cart.objects.filter(user=request.user)
            if cart_queryset.exists():
                cart = cart_queryset.first()
            else:
                cart = Cart.objects.create(user=request.user)
                cart.schedule_deletion()  # Schedule deletion for anonymous users

    def get_random_products(self):
        """Get random products for display"""
        if not self.request.user.is_staff:
            random_products = Product.objects.filter(count__gt=0)
            random_products = random.sample(list(random_products), 4)
        else:
            random_products = random.sample(list(Product.objects.all()), 4)
        return random_products


class SearchView(BaseProductView):
    """ View for searching products and displaying search results """

    @staticmethod
    def get(request):
        """ Handle GET request for search view """
        query = request.GET.get('q')
        product_list = Product.objects.filter(Q(name__icontains=query) | Q(description__icontains=query))

        if not request.user.is_staff:
            product_list = product_list.filter(count__gt=0)

        product_list = product_list.order_by('-created_at')
        paginator = Paginator(product_list, 12)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'query': query,
            'page_obj': page_obj,
            'product_list': product_list,
        }

        if not product_list.exists():
            return redirect('404')

        return render(request, 'pages/search_results.html', context)


class ProductHomeListView(BaseProductView):
    """ View for displaying a list of products on the home page """

    @staticmethod
    def get(request):
        """ Handle GET request for home/product list view """
        queryset = Product.objects.filter(active=True).order_by('?')

        if not request.user.is_staff:
            queryset = queryset.filter(count__gt=0)

        paginator = Paginator(queryset, 12)
        page_number = request.GET.get('page')
        products = paginator.get_page(page_number)
        return render(request, 'pages/home.html', {'products': products})


class CancelProduct(TemplateView):
    """ View for rendering an error page """
    template_name = 'pages/not_found.html'

    def get_context_data(self, **kwargs):
        """ Get context data for the error page """
        context = super().get_context_data(**kwargs)
        context['error_message'] = self.request.GET.get('error_message', '')
        return context


class PaymentProcessor:
    """ Utility class for processing payments """

    @staticmethod
    def process_payment(product, token, request):
        """ Process a payment for a product """
        amount = int(product.price * 100)

        if product.count <= 0:
            error_message = "Product is out of stock."
            return False, error_message

        try:
            charge = stripe.Charge.create(
                amount=amount,
                currency="usd",
                source=token,
                description=product.name,
            )
        except stripe.error.CardError as e:
            return False, e.user_message

        # Reduce the product count only after a successful Stripe charge
        product.count -= 1
        product.save()

        # Get the email from the Stripe charge object
        user_email = charge.source["name"]

        # Convert the product image to base64
        product_image_base64 = None
        if product.photos.exists():
            product_image = product.photos.first().image
            with open(product_image.path, "rb") as image_file:
                product_image_base64 = base64.b64encode(image_file.read()).decode()

        # Send the email after a successful payment
        email_context = {
            "product": product,
            "user": request.user,
            "total_price": product.price,
            "products": [
                {
                    "id": product.id,
                    "name": product.name,
                    "description": product.description,
                    "count": 1,
                    "price": product.price,
                    "image_base64": product_image_base64,
                }
            ],
        }
        EmailSender.send_inline_photo_email(user_email, email_context)

        return True, None


class PaymentView(CartMixin, View):
    """ Detail views of product and Payment """

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        cart = self.get_cart(request)

        in_cart = CartProduct.objects.filter(cart=cart, product=product).exists()
        cart_product_count = CartProduct.objects.filter(cart=cart).count()

        if cart_product_count >= 10:
            messages.error(request, 'You have reached the maximum limit of 10 products in your cart.')

        if not request.user.is_staff:
            random_products = Product.objects.filter(count__gt=0)
            random_products = random.sample(list(random_products), 4)
        else:
            random_products = random.sample(list(Product.objects.all()), 4)

        if product.count < 1:
            error_url = reverse('404')
            return redirect(error_url)

        context = {
            "product": product,
            "stripe_public_key": settings.STRIPE_PUBLIC_KEY,
            "random_products": random_products,
            "in_cart": in_cart,
            "cart_product_count": cart_product_count,
        }

        return render(request, "pages/product_detail.html", context)

    @staticmethod
    def post(request, product_id):
        product = get_object_or_404(Product, id=product_id)
        token = request.POST.get("stripeToken")

        payment_processor = PaymentProcessor()
        success, error_message = payment_processor.process_payment(product, token, request)

        if not success:
            return redirect(reverse('404') + f'?error_message={error_message}')

        return render(request, "pages/payment_success.html")


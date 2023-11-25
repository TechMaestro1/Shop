import stripe

from django.conf import settings
from django.urls import reverse

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, serializers, status

from E_Shop_API.E_Shop_Cart.models import Cart, CartProduct, Product
from E_Shop_API.E_Shop_Cart.serializers import CartProductSerializer

stripe.api_key = settings.STRIPE_SECRET_KEY


class CartMixin:
    """ Mixin to get the cart based on user authentication """

    @staticmethod
    def get_cart(request):
        user = request.user
        if user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user=user)
            cart.schedule_deletion()  # Schedule deletion for authenticated users (celery)
            return cart


class CartProductAPIView(generics.CreateAPIView, generics.UpdateAPIView, generics.DestroyAPIView):
    """ API view for adding, updating, and deleting products in the cart """
    serializer_class = CartProductSerializer

    def get_object(self):
        cart_product_id = self.kwargs['cart_product_id']

        try:
            product = Product.objects.get(id=cart_product_id)
        except Product.DoesNotExist:
            raise serializers.ValidationError('Product not found')

        user = self.request.user
        cart = self.get_cart(user)

        try:
            cart_product = CartProduct.objects.get(cart=cart, product=product)
        except CartProduct.DoesNotExist:
            cart_product = CartProduct.objects.create(cart=cart, product=product)

        return cart_product

    def post(self, request, *args, **kwargs):
        cart_product = self.get_object()

        quantity = request.data.get('quantity', 1)

        if not isinstance(quantity, int) or quantity < 1:
            return Response({'error': 'Invalid quantity'}, status=status.HTTP_400_BAD_REQUEST)

        if self.is_cart_full(cart_product.cart):
            return Response({'error': 'Maximum limit of 10 products reached'}, status=status.HTTP_400_BAD_REQUEST)

        if cart_product.product.count < quantity:
            return Response({'error': 'Quantity exceeds available count'}, status=status.HTTP_400_BAD_REQUEST)

        if cart_product.quantity > 0:
            return Response({'error': f'Product {cart_product.product.name} already in cart'},
                            status=status.HTTP_400_BAD_REQUEST)

        cart_product.quantity += quantity
        cart_product.save()

        serializer = self.get_serializer(cart_product)
        response_data = {
            'message': f'Product {cart_product.product.name} added to cart',
            'data': serializer.data
        }
        return Response(response_data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        cart_product = self.get_object()

        quantity = request.data.get('quantity')

        if quantity is not None:
            if not isinstance(quantity, int) or quantity < 1:
                return Response({'error': 'Invalid quantity'}, status=status.HTTP_400_BAD_REQUEST)

            if cart_product.product.count < quantity:
                return Response({'error': 'Quantity exceeds available count'}, status=status.HTTP_400_BAD_REQUEST)

            return self.update_cart_product_quantity(cart_product, quantity)

        return Response({'message': 'No changes detected'}, status=status.HTTP_200_OK)

    def update_cart_product_quantity(self, cart_product, quantity):
        cart_product.quantity = quantity
        cart_product.save()

        serializer = self.get_serializer(cart_product)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        cart_product = self.get_object()
        cart_product.delete()

        return Response({'message': 'Product removed from cart'}, status=status.HTTP_200_OK)

    @staticmethod
    def is_cart_full(cart):
        return cart.cart.count() >= 10

    @staticmethod
    def get_cart(user):
        if user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user=user)
            cart.schedule_deletion()
            return cart


class CartProductListAPIView(generics.ListAPIView):
    """ List of Products in Cart """
    serializer_class = CartProductSerializer

    def get_queryset(self):
        cart = self.get_cart()
        return cart.cart.all()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        cart_total_price = self.calculate_cart_total_price(queryset)

        response_data = serializer.data
        response_data.append({"total_cart_price": cart_total_price})

        return Response(response_data, status=status.HTTP_200_OK)

    @staticmethod
    def calculate_cart_total_price(cart_products):
        total_price = sum(cart_product.subtotal() for cart_product in cart_products)
        return total_price

    def get_cart(self):
        user = self.request.user
        if user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user=user)
            cart.schedule_deletion()  # celery
            return cart


class PaymentCartAPIView(APIView):
    """ Processing the cart payment """

    @staticmethod
    def get_cart(request):
        user = request.user

        if user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user=user)
            cart.schedule_deletion()  # Schedule deletion for authenticated users (celery)
            return cart
        return None

    def post(self, request):
        cart = self.get_cart(request)

        if cart is None:
            return Response({'error': 'User is not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

        cart_products = CartProduct.objects.filter(cart=cart)
        line_items = self.create_line_items(cart_products)

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

        self.update_session_data(request, cart, checkout_session)

        return Response({'url': checkout_session.url})

    @staticmethod
    def create_line_items(cart_products):
        line_items = []
        for cart_product in cart_products:
            product = cart_product.product
            if product.count < cart_product.quantity:
                return Response({'error': 'The quantity of the product is more than the available amount'})

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

        return line_items

    @staticmethod
    def update_session_data(request, cart, checkout_session):
        request.session['checkout_session_id'] = checkout_session.id
        request.session['cart_id'] = str(cart.id)
        request.session.modified = True

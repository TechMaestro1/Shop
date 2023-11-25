# python manage.py test E_Shop_API.E_Shop_Cart.tests.test_views
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.test import TestCase
from rest_framework.test import APIRequestFactory

from E_Shop_API.E_Shop_Cart.models import Cart, Product, CartProduct
from E_Shop_API.E_Shop_Cart.serializers import CartProductSerializer
from E_Shop_API.E_Shop_Cart.views import CartProductListAPIView
from E_Shop_API.E_Shop_Products.tests.helpers.test_helpers import create_product
from E_Shop_API.E_Shop_Users.tests.helpers.test_helpers import create_basic_user


class CartProductViewAPITestCase(TestCase):
    """ Test cases for the CartProduct API views """

    def setUp(self):
        """ Set up the test environment """
        self.client = APIClient()
        self.user = create_basic_user()

        self.cart = Cart.objects.create(user=self.user)
        self.product = create_product()

        self.client.force_authenticate(user=self.user)

    def tearDown(self):
        """ Tear down the test environment """
        self.client.logout()
        self.cart.delete()
        self.user.delete()
        self.product.delete()

    def create_cart_product(self, quantity):
        """ Create a CartProduct with the given quantity """
        return CartProduct.objects.create(cart=self.cart, product=self.product, quantity=quantity)

    def test_add_product_to_cart(self):
        """ Test adding a product to the cart """
        url = reverse('cart_product_api', kwargs={'cart_product_id': self.product.id})
        data = {'quantity': 3}

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check if the product is added to the cart
        cart_product = CartProduct.objects.get(cart=self.cart, product=self.product)
        self.assertEqual(cart_product.quantity, 3)

    def test_update_cart_product_quantity(self):
        """ Test updating the quantity of a product in the cart """
        cart_product = self.create_cart_product(quantity=2)
        url = reverse('cart_product_api', kwargs={'cart_product_id': self.product.id})
        data = {'quantity': 5}

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check if the cart product quantity is updated
        cart_product.refresh_from_db()
        self.assertEqual(cart_product.quantity, 5)

    def test_remove_product_from_cart(self):
        """ Test removing a product from the cart """
        cart_product = self.create_cart_product(quantity=2)
        url = reverse('cart_product_api', kwargs={'cart_product_id': self.product.id})

        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check if the cart product is removed from the cart
        with self.assertRaises(CartProduct.DoesNotExist):
            CartProduct.objects.get(cart=self.cart, product=self.product)

    def test_add_invalid_quantity(self):
        """ Test adding a product with an invalid (negative) quantity """
        url = reverse('cart_product_api', kwargs={'cart_product_id': self.product.id})
        response = self.client.post(url, {'quantity': -1}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_product_with_exceeding_quantity(self):
        """ Test adding a product with a quantity exceeding the available count """
        url = reverse('cart_product_api', kwargs={'cart_product_id': self.product.id})
        response = self.client.post(url, {'quantity': 21}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CartProductListAPIViewTestCase(TestCase):
    def setUp(self):
        """ Set up the test environment """
        self.factory = APIRequestFactory()
        self.user = create_basic_user()
        self.cart = Cart.objects.create(user=self.user)
        self.product1 = Product.objects.create(name='Product 1', price=10, count=2)
        self.product2 = Product.objects.create(name='Product 2', price=15, count=1)
        self.cart_product1 = CartProduct.objects.create(product=self.product1, cart=self.cart, quantity=2)
        self.cart_product2 = CartProduct.objects.create(product=self.product2, cart=self.cart, quantity=1)

    def test_cart_product_list_api_view(self):
        """ Test the cart product list API view with valid data """
        url = '/cart/'
        request = self.factory.get(url)
        request.user = self.user

        response = CartProductListAPIView.as_view()(request)
        self.assertEqual(response.status_code, 200)

        expected_data = CartProductSerializer([self.cart_product1, self.cart_product2], many=True).data
        expected_data.append({"total_cart_price": 35.0})
        self.assertEqual(response.data, expected_data)

    def test_cart_product_list_api_view_invalid_product(self):
        """ Test the cart product list API view with an invalid product """
        url = '/cart/'
        request = self.factory.get(url)
        request.user = self.user

        valid_product = create_product()

        self.cart_product1.product = valid_product
        self.cart_product1.save()

        response = CartProductListAPIView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data) - 1, 2)

    def test_cart_product_list_api_view_empty_cart(self):
        """ Test the cart product list API view with an empty cart """
        url = '/cart/'
        request = self.factory.get(url)
        request.user = self.user

        self.cart.cart.all().delete()

        response = CartProductListAPIView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

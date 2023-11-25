# python manage.py test E_Shop_Frontend.Cart.tests.test_views
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from E_Shop_API.E_Shop_Cart.models import Cart, CartProduct
from E_Shop_API.E_Shop_Products.tests.helpers.test_helpers import create_product
from E_Shop_API.E_Shop_Users.tests.helpers.test_helpers import create_basic_user
from E_Shop_Frontend.Products.tests.test_views import TestHelpers


class CartDetailViewTestCase(TestCase):
    """ Test cases for the CartDetailView """

    def setUp(self):
        """ Set up the test environment """
        self.user = create_basic_user()
        self.client.login(username='User', password='UserPass123', email='user@gmail.com')

        self.product = create_product()

        self.cart = Cart.objects.create(user=self.user)
        self.cart_product = CartProduct.objects.create(cart=self.cart, product=self.product, quantity=2)

    def test_cart_detail_authenticated_user(self):
        """ Test cart detail view for an authenticated user with items in the cart """
        response = self.client.get(reverse('cart_detail'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/cart_detail.html')
        self.assertEqual(response.context['cart'], self.cart)
        self.assertIn(self.cart_product, response.context['cart_products'])

    def test_cart_detail_authenticated_user_empty_cart(self):
        """ Test cart detail view for an authenticated user with an empty cart """
        self.cart_product.delete()
        response = self.client.get(reverse('cart_detail'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/cart_detail.html')
        self.assertEqual(response.context['cart'], self.cart)
        self.assertNotIn(self.cart_product, response.context['cart_products'])

    def test_cart_detail_unauthenticated_user(self):
        """ Test cart detail view for an unauthenticated user """
        self.client.logout()
        response = self.client.get(reverse('cart_detail'))
        self.assertRedirects(response, reverse('login'))


class AddToCartViewTest(TestCase):
    """ Test cases for the AddToCartView """

    def setUp(self):
        """ Set up the test environment """
        self.user = create_basic_user()
        self.product = create_product()

    def test_add_product_to_cart_authenticated_user(self):
        """ Test adding a product to the cart for an authenticated user """
        self.client.login(username='user@gmail.com', password='UserPass123')
        response = self.client.get(reverse('add_to_cart', args=[str(self.product.id)]))
        self.assertRedirects(response, reverse('cart_detail'))
        user_cart = Cart.objects.get(user=self.user)
        cart_product = CartProduct.objects.get(cart=user_cart, product=self.product)
        self.assertEqual(cart_product.quantity, 1)  # By default, quantity is 1

    def test_add_product_to_cart_authenticated_user_with_quantity(self):
        """ Test adding a product to the cart for an authenticated user with a specified quantity """
        self.client.login(username='user@gmail.com', password='UserPass123')
        quantity = 1
        response = self.client.get(reverse('add_to_cart', args=[str(self.product.id)]), {'quantity': quantity})
        self.assertRedirects(response, reverse('cart_detail'))
        user_cart = Cart.objects.get(user=self.user)
        cart_product = CartProduct.objects.get(cart=user_cart, product=self.product)
        self.assertEqual(cart_product.quantity, quantity)

    def test_add_product_to_cart_unauthenticated_user(self):
        """ Test adding a product to the cart for an unauthenticated user """
        response = self.client.get(reverse('add_to_cart', args=[str(self.product.id)]))
        self.assertRedirects(response, reverse('login'))
        user_cart = Cart.objects.filter(user=self.user)
        self.assertFalse(user_cart.exists())


class UpdateCartViewTest(TestCase):
    """ Test cases for the UpdateCartView """

    def setUp(self):
        """ Set up the test environment """
        self.user = create_basic_user()
        self.product = create_product()
        self.cart = Cart.objects.create(user=self.user)

    def test_add_to_cart(self):
        """ Test adding a product to the cart """
        self.client.login(username='user@gmail.com', password='UserPass123')
        response = self.client.post(reverse('update_cart', args=[str(self.product.id)]), {'action': 'add'})
        self.assertRedirects(response, reverse('cart_detail'))
        cart_product = CartProduct.objects.get(cart=self.cart, product=self.product)
        self.assertEqual(cart_product.quantity, 1)

    def test_remove_from_cart(self):
        """ Test removing a product from the cart """
        self.client.login(username='user@gmail.com', password='UserPass123')
        cart_product = CartProduct.objects.create(cart=self.cart, product=self.product, quantity=2)
        response = self.client.post(reverse('update_cart', args=[str(self.product.id)]), {'action': 'remove'})
        self.assertRedirects(response, reverse('cart_detail'))
        cart_product.refresh_from_db()
        self.assertEqual(cart_product.quantity, 1)

    def test_update_cart_quantity(self):
        """ Test updating the quantity of a product in the cart """
        self.client.login(username='user@gmail.com', password='UserPass123')
        cart_product = CartProduct.objects.create(cart=self.cart, product=self.product, quantity=2)
        new_quantity = 3
        response = self.client.post(reverse('update_cart', args=[str(self.product.id)]),
                                    {'action': 'update', 'quantity': new_quantity})
        self.assertRedirects(response, reverse('cart_detail'))
        cart_product.refresh_from_db()
        self.assertEqual(cart_product.quantity, new_quantity)


class RemoveCartViewTest(TestCase):
    """ Test cases for the RemoveCartView """

    def setUp(self):
        """ Set up the test environment """
        self.user = create_basic_user()
        self.product = create_product()

        self.cart = Cart.objects.create(user=self.user)
        self.cart_product = CartProduct.objects.create(cart=self.cart, product=self.product, quantity=2)

    def test_remove_from_cart_get(self):
        """ Test removing a product from the cart using a GET request """
        self.client.login(username='user@gmail.com', password='UserPass123')
        response = self.client.get(reverse('remove_from_cart', args=[str(self.product.id)]))
        self.assertRedirects(response, reverse('cart_detail'))
        cart_product_exists = CartProduct.objects.filter(cart=self.cart, product=self.product).exists()
        self.assertFalse(cart_product_exists)

    def test_remove_from_cart_post(self):
        """ Test removing a product from the cart using a POST request """
        self.client.login(username='user@gmail.com', password='UserPass123')
        response = self.client.post(reverse('remove_from_cart', args=[str(self.product.id)]))
        self.assertRedirects(response, reverse('cart_detail'))
        cart_product_exists = CartProduct.objects.filter(cart=self.cart, product=self.product).exists()
        self.assertFalse(cart_product_exists)


class EmptyCartViewTest(TestCase):
    """ Test cases for the EmptyCartView """

    def setUp(self):
        """ Set up the test environment """
        self.user = create_basic_user()
        self.product = create_product()

        self.cart = Cart.objects.create(user=self.user)
        self.cart_product = CartProduct.objects.create(cart=self.cart, product=self.product, quantity=2)

    def test_empty_cart(self):
        """ Test emptying the cart"""
        self.client.login(username='user@gmail.com', password='UserPass123')
        response = self.client.get(reverse('empty_cart'))
        self.assertRedirects(response, reverse('cart_detail'))
        cart_products_exist = CartProduct.objects.filter(cart=self.cart).exists()
        self.assertFalse(cart_products_exist)


class PaymentCartViewTest(TestCase):
    """ Test cases for the PaymentCartViewTest """

    def setUp(self):
        """ Set up the test environment """
        self.user = create_basic_user()
        self.client.login(username='user@gmail.com', password='UserPass123')

        self.cart = Cart.objects.create(user=self.user)
        self.product = create_product()

        self.cart_product = CartProduct.objects.create(cart=self.cart, product=self.product, quantity=2)

        self.stripe_token = TestHelpers.generate_stripe_token()

    @patch('stripe.checkout.Session.create')
    def test_payment_cart_insufficient_product_quantity(self, mock_checkout_session_create):
        self.product.count = 1
        self.product.save()

        mock_checkout_session_create.return_value = {
            'id': 'test_session_id',
            'url': 'https://example.com/payment/checkout',
        }

        self.client.login(username='user@gmail.com', password='UserPass123')
        response = self.client.post(reverse('payment_cart'))

        expected_url = reverse(
            '404') + '?error_message=Check+your+cart%2C+the+quantity+of+the+product+is+more+than+the+available+amount'
        self.assertRedirects(response, expected_url)

    def test_payment_cart_view(self):
        url = reverse('payment_cart')
        response = self.client.post(url, {'stripe_token': self.stripe_token})
        self.assertEqual(response.status_code, 302)  # Check if it redirects (you can adjust this as needed)
        # Add more assertions based on your application's logic and expected behavior


class PaymentSuccessViewTest(TestCase):
    """ Test cases for the PaymentSuccessView """

    def setUp(self):
        """ Set up the test environment """
        self.user = create_basic_user()
        self.cart = Cart.objects.create(user=self.user)

        self.product = create_product()

        self.cart_product = CartProduct.objects.create(cart=self.cart, product=self.product, quantity=2)

    def test_payment_success_with_session_data(self):
        """ Test payment success with session data """
        self.client.login(username='user@gmail.com', password='UserPass123')
        self.client.session['checkout_session_id'] = 'test_session_id'
        self.client.session['cart_id'] = str(self.cart.id)
        self.client.session.modified = True
        response = self.client.get(reverse('payment_success'))
        self.assertEqual(response.status_code, 302)
        self.assertNotIn('checkout_session_id', self.client.session)
        self.assertNotIn('cart_id', self.client.session)
        cart = Cart.objects.get(id=self.cart.id)
        self.assertEqual(cart.cart.all().count(), 1)

    def test_payment_success_without_session_data(self):
        """ Test payment success without session data """
        self.client.login(username='user@gmail.com', password='UserPass123')
        response = self.client.get(reverse('payment_success'))
        self.assertRedirects(response, reverse('404'))

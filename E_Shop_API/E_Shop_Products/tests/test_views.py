# python manage.py test E_Shop_API.E_Shop_Products.tests.test_views
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate

from E_Shop_API.E_Shop_Products.models import Product
from E_Shop_API.E_Shop_Products.views import ProductCreateView, ProductListView
from E_Shop_API.E_Shop_Users.tests.helpers.test_helpers import create_admin_user, create_basic_user
from E_Shop_Frontend.Cart.tests.test_views import create_product


class ProductCreateViewTestCase(TestCase):
    """ Test cases for the ProductCreateView """

    @classmethod
    def setUpTestData(cls):
        """ Set up test data and users """
        cls.factory = APIRequestFactory()
        cls.admin_user = create_admin_user()
        cls.non_admin_user = create_basic_user()

    def create_product(self, user, status_code, expected_count):
        """ Helper method to create a product and check the response """
        url = reverse('create_product')
        request = self.factory.post(url, {'name': 'Test Product', 'price': 10.0, 'count': 20})
        force_authenticate(request, user=user)
        response = ProductCreateView.as_view()(request)
        self.assertEqual(response.status_code, status_code)
        self.assertEqual(Product.objects.count(), expected_count)

    def test_create_product_admin(self):
        """ Test creating a product with an admin user """
        self.create_product(self.admin_user, status.HTTP_201_CREATED, 1)

    def test_create_product_non_admin(self):
        """ Test creating a product with a non-admin user """
        self.create_product(self.non_admin_user, status.HTTP_403_FORBIDDEN, 0)


class ProductListViewTestCase(TestCase):
    """ Test cases for the ProductListView """

    def setUp(self):
        """ Set up test data and users """
        self.factory = APIRequestFactory()
        self.admin_user = create_admin_user()
        self.non_admin_user = create_basic_user()

    def test_product_list_admin(self):
        """ Test getting the product list with an admin user """
        url = reverse('all_product')
        request = self.factory.get(url)
        force_authenticate(request, user=self.admin_user)
        response = ProductListView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_product_list_non_admin(self):
        """ Test getting the product list with a non-admin user """
        url = reverse('all_product')
        request = self.factory.get(url)
        force_authenticate(request, user=self.non_admin_user)
        response = ProductListView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ProductViewTestCase(APITestCase):
    """ Test cases for the ProductView """

    @classmethod
    def setUpTestData(cls):
        """ Set up test data and users """
        cls.admin_user = create_admin_user()
        cls.product = create_product()

    def test_get_product_admin(self):
        """ Test getting a product with an admin user """
        url = reverse('product_detail', args=[self.product.id])
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_product_non_admin(self):
        """ Test getting a product with a non-admin user """
        url = reverse('product_detail', args=[self.product.id])
        self.client.force_authenticate(user=create_basic_user())
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_put_product_admin(self):
        """ Test updating a product with an admin user using PUT """
        url = reverse('product_detail', args=[self.product.id])
        data = {'name': 'Updated Product', 'price': 15.0, 'count': 25}
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Product.objects.get(id=self.product.id).name, 'Updated Product')

    def test_patch_product_admin(self):
        """ Test updating a product with an admin user using PATCH """
        url = reverse('product_detail', args=[self.product.id])
        data = {'price': 15.0}
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Product.objects.get(id=self.product.id).price, 15.0)

    def test_delete_product_admin(self):
        """ Test deleting a product with an admin user """
        url = reverse('product_detail', args=[self.product.id])
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Product.objects.filter(id=self.product.id).exists())

    def test_delete_product_non_admin(self):
        """ Test attempting to delete a product with a non-admin user """
        url = reverse('product_detail', args=[self.product.id])
        self.client.force_authenticate(user=create_basic_user())
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

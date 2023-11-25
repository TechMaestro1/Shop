# python manage.py test E_Shop_API.E_Shop_Products.tests.test_urls
from django.urls import reverse
from django.test import TestCase


class UrlsTestCase(TestCase):
    def test_create_product_url(self):
        """ Test if the URL for creating a product is correctly reversed """
        url = reverse('create_product')
        expected_url = '/api/create-product/'
        self.assertEqual(url, expected_url)

    def test_product_detail_url(self):
        """ Test if the URL for a specific product's detail view is correctly reversed """
        product_id = 'eeb52aec-1b21-4dcc-956c-b3dd6e48c229'  # Replace id with a valid UUID
        url = reverse('product_detail', args=[product_id])
        expected_url = f'/api/product/{product_id}/'
        self.assertEqual(url, expected_url)

    def test_all_product_url(self):
        """ Test if the URL for listing all products is correctly reversed """
        url = reverse('all_product')
        expected_url = '/api/products/'
        self.assertEqual(url, expected_url)

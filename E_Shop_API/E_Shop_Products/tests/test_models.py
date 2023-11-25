# python manage.py test E_Shop_API.E_Shop_Products.tests.test_models
from django.test import TestCase
from django.core.exceptions import ValidationError
from E_Shop_API.E_Shop_Products.models import Product, ProductImage
from E_Shop_API.E_Shop_Products.tests.helpers.test_helpers import create_product


class ProductModelTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        """ Create a Product instance for testing """
        cls.product = create_product()

    def test_name_label(self):
        """ Test if the name field's verbose_name is 'Name' """
        field_label = self.product._meta.get_field('name').verbose_name
        self.assertEqual(field_label, 'Name')

    def test_description_blank(self):
        """Test if the description field allows blank values"""
        field = self.product._meta.get_field('description')
        self.assertTrue(field.blank)

    def test_price_validation(self):
        """ Test price validation: should raise a ValidationError for negative price """
        with self.assertRaises(ValidationError):
            self.product.price = -10.0
            self.product.full_clean()  # This will trigger validation

    def test_count_validation(self):
        """ Test count validation: should raise a ValidationError for negative count """
        with self.assertRaises(ValidationError) as context:
            self.product.count = -20
            self.product.full_clean()  # This will trigger validation

    def test_str_representation(self):
        """ Test if the string representation of a Product instance is its name """
        self.assertEqual(str(self.product), 'Test Product')


class ProductImageModelTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        """ Create a Product and ProductImage instances for testing """
        cls.product = create_product()

        cls.product_image = ProductImage.objects.create(
            product=cls.product,
            image='static/img/bin.png',
        )

    def test_product_image_relationship(self):
        """ Test if the product_image's product field is correctly related to a product """
        self.assertEqual(self.product_image.product, self.product)

    def test_image_upload_to(self):
        """ Test if the image field's upload_to attribute is 'photos' """
        field = self.product_image._meta.get_field('image')
        self.assertEqual(field.upload_to, 'photos')

    def test_str_representation(self):
        """ Test if the string representation of a ProductImage instance is its image filename """
        expected_str = str(self.product_image.image)
        self.assertEqual(str(self.product_image), expected_str)

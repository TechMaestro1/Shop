from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.conf import settings
import base64
from email.mime.image import MIMEImage


class EmailSender:
    """ Utility class for sending emails """

    @classmethod
    def send_inline_photo_email(cls, user_email, email_context):
        """ Send an email with an inline photo """
        subject = 'Payment Confirmation'
        html_message = render_to_string('email_templates/payment_confirmation.html', email_context)
        plain_message = strip_tags(html_message)

        # Create the email message
        email = EmailMultiAlternatives(subject, plain_message, settings.DEFAULT_FROM_EMAIL, [user_email])
        email.attach_alternative(html_message, 'text/html')

        # Attach the first product image to the email as inline content
        products = email_context['products']
        for product in products:
            image_base64 = product.get('image_base64')
            if image_base64:
                email_image = MIMEImage(base64.b64decode(image_base64))
                email_image.add_header('Content-ID', f'<inline_image_{product["id"]}>')
                email.attach(email_image)
                break  # Attach only the first image and then exit the loop

        # Send the email
        email.send()

from datetime import datetime, timedelta
from celery import shared_task

from django.apps import apps
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail, EmailMultiAlternatives

from E_Shop_API.E_Shop_Users.models import Clients
from E_Shop_config.settings import EMAIL_HOST_USER


@shared_task
def send_confirm_email(user_id, domain):
    """ Send confirm letter """
    user = get_user_model().objects.get(pk=user_id)
    mail_subject = 'Confirm Your Account'
    # Render the HTML content of the email template
    message_html = render_to_string('email_templates/confirm_email.html', {
        'user': user,
        'domain': domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': default_token_generator.make_token(user),
    })

    # Create both text and HTML versions of the email
    email = EmailMultiAlternatives(mail_subject, '', to=[user.email])
    email.attach_alternative(message_html, "text/html")
    email.send()


@shared_task
def send_new_user_notification():
    """ Send information about new user once per day """

    current_date = datetime.now()
    previous_date = current_date - timedelta(days=1)

    new_users = Clients.objects.filter(date_joined__gte=previous_date, date_joined__lt=current_date)

    subject = 'New User Registration Notification'
    message = 'Newly registered users:\n\n'
    for user in new_users:
        message += f'Name - {user.username}, Email - ({user.email})\n'

    send_mail(subject, message, EMAIL_HOST_USER, [EMAIL_HOST_USER, ])


@shared_task
def delete_cart(cart_id):
    """ Auto delete cart after 1 day """

    Cart = apps.get_model('E_Shop_Cart', 'Cart')

    try:
        cart = Cart.objects.get(id=cart_id)
        if cart.created_at <= timezone.now() - timedelta(days=1):
            cart.delete()
        else:
            delete_cart.apply_async((cart_id,), eta=cart.created_at + timedelta(days=1))

    except Cart.DoesNotExist:
        print(f"Cart {cart_id} does not exist.")

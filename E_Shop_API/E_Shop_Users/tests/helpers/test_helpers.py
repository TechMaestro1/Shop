from E_Shop_API.E_Shop_Users.models import Clients


def create_admin_user():
    """ Create and return an admin user for testing """
    return Clients.objects.create_user(
        first_name='Admin',
        last_name='Admin',
        email='admin@gmail.com',
        username='admin',
        password='AdminPass123',
        is_staff=True,
        is_superuser=True,
    )


def create_basic_user():
    """ Create and return a basic user for testing """
    return Clients.objects.create_user(
        username='User',
        first_name='User',
        last_name='User',
        email='user@gmail.com',
        password='UserPass123',
        is_staff=False,
        is_superuser=False,
    )

import os
import django
from pathlib import Path
from django.core.management import call_command
from django.conf import settings
import shutil

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'E_Shop_config.settings')

django.setup()


def copy_images():
    # Define source and target directories
    fixtures_dir = Path('My_fixtures/photos')
    target_dir = Path(settings.MEDIA_ROOT) / 'photos'

    # Create target directory if it doesn't exist
    target_dir.mkdir(parents=True, exist_ok=True)

    # Iterate over files in the source directory
    for image_path in fixtures_dir.iterdir():
        if image_path.is_file():
            # Construct the target path
            target_path = target_dir / image_path.name
            # Copy the file to the target path
            shutil.copy(str(image_path), str(target_path))


def load_fixture(fixture_name):
    # Load fixture data using Django management command
    call_command('loaddata', f'My_fixtures/{fixture_name}.json')


# Copy images from fixtures to the media directory
copy_images()

# Load fixture data for products and users
load_fixture('my_products_data')
load_fixture('my_users_data')

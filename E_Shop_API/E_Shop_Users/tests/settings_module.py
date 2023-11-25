import os
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'E_Shop_config.settings')
import django

django.setup()

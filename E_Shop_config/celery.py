from __future__ import absolute_import, unicode_literals

import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', "E_Shop_config.settings")

app = Celery('E_Shop_config')
app.conf.enable_utc = False

app.conf.update(timezone='Europe/Kiev')
app.config_from_object("django.conf:settings", namespace='CELERY')

app.autodiscover_tasks()


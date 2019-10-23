import os
from django.conf import settings
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'custom_settings')

celery_app = Celery('service_runner')
celery_app.config_from_object(settings)
celery_app.autodiscover_tasks()

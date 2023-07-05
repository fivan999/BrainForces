import os

import celery
import django.conf


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'brainforces.settings')
app = celery.Celery(
    'brainforces', broker=django.conf.settings.CELERY_BROKER_URL
)
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

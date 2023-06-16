import os

import celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'brainforces.settings')
app = celery.Celery('brainforces')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

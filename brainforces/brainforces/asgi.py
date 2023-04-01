import os

from django.core import asgi

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'brainforces.settings')

application = asgi.get_asgi_application()

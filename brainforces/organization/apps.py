import django.apps


class OrganizationConfig(django.apps.AppConfig):
    """базовый класс приложения organization"""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'organization'
    verbose_name = 'организация'

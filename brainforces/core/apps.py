import django.apps


class CoreConfig(django.apps.AppConfig):
    """базовый класс для приложения core"""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = 'кор'

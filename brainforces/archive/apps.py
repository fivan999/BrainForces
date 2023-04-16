import django.apps


class ArchiveConfig(django.apps.AppConfig):
    """базовый класс для приложения Archive"""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'archive'
    verbose_name = 'архив'

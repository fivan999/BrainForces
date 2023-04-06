import django.apps


class HomepageConfig(django.apps.AppConfig):
    """базовый класс для приложения homepage"""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'homepage'
    verbose_name = 'главная'

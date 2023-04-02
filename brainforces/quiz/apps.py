from django.apps import AppConfig


class QuizConfig(AppConfig):
    """базовый класс для приложения Quiz"""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'quiz'
    verbose_name = 'викторина'

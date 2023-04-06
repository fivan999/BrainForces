import django.contrib.auth.models
import django.core.exceptions
import django.db.models


class QuizManager(django.db.models.Manager):
    """менеджер модели Quiz"""

    def get_only_useful_list_fields(self) -> django.db.models.QuerySet:
        """только нужные поля для списка викторин"""
        return self.get_queryset().only(
            'name',
            'description',
            'creator',
            'duration',
            'status',
            'start_time',
        )

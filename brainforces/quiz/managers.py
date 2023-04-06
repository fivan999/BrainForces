import django.contrib.auth.models
import django.core.exceptions
import django.db.models


class QuizManager(django.db.models.Manager):
    """менеджер модели Quiz"""

    def get_only_useful_list_fields(self) -> django.db.models.QuerySet:
        """только нужные поля для списка викторин"""
        return (
            self.get_queryset()
            .select_related('creator')
            .only(
                'name',
                'description',
                'creator__username',
                'duration',
                'status',
                'start_time',
            )
            .order_by('-id')
        )

import django.contrib.auth.models
import django.core.exceptions
import django.db.models


class QuizManager(django.db.models.Manager):
    """менеджер модели Quiz"""

    def get_only_useful_list_fields(self) -> django.db.models.QuerySet:
        """только нужные поля для списка викторин на главной"""
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
            .order_by('-start_time')
        )


class UserAnswerManager(django.db.models.Manager):
    """менеджер модели UserAnswer"""

    def get_only_useful_answer_fields(self) -> django.db.models.QuerySet:
        """поля для отображения в профиле пользователя"""
        return (
            self.get_queryset()
            .select_related('user', 'question')
            .only(
                'user__username',
                'question__id',
                'question__name',
                'is_correct',
                'time_answered',
            )
        )

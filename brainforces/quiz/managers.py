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

    def get_only_useful_list_fields(self) -> django.db.models.QuerySet:
        """поля для отображения посылок пользователя"""
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


class QuizResultsManager(django.db.models.Manager):
    """менеджер модели QuizResults"""

    def get_only_useful_list_fields(self) -> django.db.models.QuerySet:
        """
        поля для вывода списка соревнований,
        в которых участвовал пользователь
        """
        return (
            self.get_queryset()
            .select_related('user', 'quiz')
            .only(
                'rating_before',
                'rating_after',
                'user__username',
                'quiz__name',
                'quiz__start_time',
                'solved',
                'place',
            )
        )


class QuestionManager(django.db.models.Manager):
    """менеджер модели Question"""

    def get_only_useful_list_fields(self) -> django.db.models.QuerySet:
        """только нужные поля для списка архивных вопросов"""
        return (
            self.get_queryset()
            .filter(quiz__status=3)
            .only(
                'id',
                'name',
                'difficulty',
            )
            .order_by('difficulty')
        )

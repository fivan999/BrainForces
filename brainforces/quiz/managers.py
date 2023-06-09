import django.db.models
import django.db.models.expressions
import django.utils.timezone


class QuizManager(django.db.models.Manager):
    """менеджер модели Quiz"""

    def get_active_and_published_quizzes(self) -> None:
        """получаем викторины, к=организации которых активные"""
        return self.get_queryset().filter(
            organized_by__is_active=True, is_published=True
        )

    def get_only_useful_list_fields(self) -> django.db.models.QuerySet:
        """только нужные поля для списка викторин на главной"""
        return (
            self.get_active_and_published_quizzes()
            .select_related('creator', 'organized_by')
            .only(
                'name',
                'description',
                'creator__username',
                'duration',
                'start_time',
                'organized_by__name',
                'is_private',
                'is_ended',
            )
            .order_by('-start_time')
        )

    def filter_user_access(
        self, user_pk: int, org_pk: int = -1
    ) -> django.db.models.QuerySet:
        """
        доступ пользователя к квизу
        либо оргация не приватная,
        либо пользователь ее участник
        """
        posts_queryset = self.get_only_useful_list_fields().filter(
            django.db.models.Q(organized_by__is_private=False)
            & django.db.models.Q(is_private=False)
            | django.db.models.Q(organized_by__users__user__pk=user_pk)
        )
        if org_pk != -1:
            posts_queryset = posts_queryset.filter(organized_by__pk=org_pk)
        return posts_queryset.distinct()


class UserAnswerManager(django.db.models.Manager):
    """менеджер модели UserAnswer"""

    def get_active_and_published_answers(self) -> django.db.models.QuerySet:
        """ответы к опубликованным викторинам с активными организациями"""
        return self.get_queryset().filter(
            question__quiz__is_published=True,
            question__quiz__organized_by__is_active=True,
        )

    def get_only_useful_list_fields(self) -> django.db.models.QuerySet:
        """поля для отображения посылок пользователя"""
        return (
            self.get_active_and_published_answers()
            .select_related('user', 'question')
            .only(
                'user__username',
                'question',
                'is_correct',
                'time_answered',
                'question__name',
            )
        )


class QuizResultsManager(django.db.models.Manager):
    """менеджер модели QuizResults"""

    def get_published_and_active_quiz_results(
        self,
    ) -> django.db.models.QuerySet:
        """результаты с опубликованной викториной и активной оргой"""
        return self.get_queryset().filter(
            quiz__is_published=True, quiz__organized_by__is_active=True
        )

    def get_only_useful_list_fields(self) -> django.db.models.QuerySet:
        """
        поля для вывода списка соревнований,
        в которых участвовал пользователь
        """
        return (
            self.get_published_and_active_quiz_results()
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

    def get_visible_questions(self) -> django.db.models.QuerySet:
        """викторина закончена, квиз не приватный и опубликованный"""
        return self.get_queryset().filter(
            quiz__start_time__lte=django.utils.timezone.now()
            - django.utils.timezone.timedelta(minutes=1)
            * django.db.models.F('quiz__duration'),
            quiz__is_private=False,
            quiz__is_published=True,
        )

    def get_only_useful_list_fields(self) -> django.db.models.QuerySet:
        """только нужные поля для списка архивных вопросов"""
        return (
            self.get_visible_questions()
            .select_related('quiz')
            .only(
                'id',
                'name',
                'difficulty',
                'quiz__id',
            )
            .order_by('difficulty')
        )

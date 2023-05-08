import django.views.generic

import quiz.models


class QuizMixin(django.views.generic.View):
    """
    дополняем контекст именем викторины и проверяем доступ пользователя:
    может ли он участвовать в викторине и решать вопросы
    статус квиза(не начат, идет, закончен)
    стартовое и конечное время квиза
    """

    def get_context_data(self, *args, **kwargs) -> dict:
        context = super().get_context_data(*args, **kwargs)
        quiz_obj = django.shortcuts.get_object_or_404(
            quiz.models.Quiz.objects.filter(
                django.db.models.Q(organized_by__is_private=False)
                & django.db.models.Q(is_private=False)
                | django.db.models.Q(
                    organized_by__users__user__pk=self.request.user.pk
                )
            ).only('is_private', 'start_time', 'duration'),
            pk=self.kwargs['pk'],
        )
        context['quiz'] = quiz_obj
        context['can_participate'] = quiz.models.QuizResults.objects.filter(
            quiz__pk=self.kwargs['pk'], user__pk=self.request.user.pk
        ).exists()
        quiz_status = quiz_obj.get_quiz_status()
        if quiz_status == 1:
            context['can_access_questions'] = False
        elif quiz_status == 2:
            context['can_access_questions'] = context['can_participate']
        else:
            context[
                'can_access_questions'
            ] = quiz.services.user_can_access_quiz(quiz_obj, self.request.user)
        context['quiz_status'] = quiz_status
        context['now_time'] = str(django.utils.timezone.now())
        context['end_time'] = str(
            quiz_obj.start_time
            + django.utils.timezone.timedelta(minutes=quiz_obj.duration)
        )
        return context


class AccessToQuizMixin(QuizMixin):
    """проверяем доступ участника к викторине"""

    def get_context_data(self, *args, **kwargs) -> dict:
        context = super().get_context_data(*args, **kwargs)
        if not context['can_access_questions']:
            raise django.http.Http404()
        return context

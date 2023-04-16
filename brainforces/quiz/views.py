import typing

import django.db.models
import django.http
import django.shortcuts
import django.views.generic

import quiz.forms
import quiz.models


class QuizDetailView(django.views.generic.DetailView):
    """детальная информация о викторине"""

    model = quiz.models.Quiz
    template_name = 'quiz/quiz_detail.html'
    context_object_name = 'quiz'

    def get_queryset(self) -> django.db.models.QuerySet:
        return (
            quiz.models.Quiz.objects.select_related('creator')
            .prefetch_related(
                django.db.models.Prefetch(
                    'quiz_question',
                    queryset=(
                        quiz.models.Question.objects.prefetch_related(
                            django.db.models.Prefetch(
                                'useranswer_question',
                                queryset=quiz.models.UserAnswer.objects.filter(
                                    user__id=self.request.user.id
                                ),
                            )
                        )
                    ),
                )
            )
            .only(
                'name',
                'description',
                'start_time',
                'duration',
                'creator__username',
                'id',
                'status',
            )
        )


class QuestionDetailView(django.views.generic.DetailView):
    """детальная информация о вопросе"""

    model = quiz.models.Question
    template_name = 'quiz/question_detail.html'
    context_object_name = 'question'
    queryset = quiz.models.Question.objects.only('name', 'text', 'difficulty')

    def get_context_data(self, *args, **kwargs) -> typing.Dict:
        """Дополняем контекст информацией об id викторины
        в которой сейчас участвуют и порядковым номером вопроса"""
        context = super(QuestionDetailView, self).get_context_data(
            *args, **kwargs
        )
        variants = quiz.models.Variant.objects.filter(
            question__id=self.kwargs['pk']
        )
        arr = []
        for variant in variants:
            arr.append((variant.id, variant.text))
        context['quiz_id'] = self.kwargs['quiz_id']
        context['question_number'] = self.kwargs['question_number']
        form = quiz.forms.AnswerForm()
        form.fields['answers'].choices = arr
        context['form'] = form
        return context

    def post(
        self, request: django.http.HttpRequest, *args, **kwargs
    ) -> django.http.HttpResponse:
        """сохраняем ответ пользователя"""
        is_correct = (
            quiz.models.Variant.objects.filter(
                pk=request.POST['answers']
            ).values('is_correct')
        )[0]['is_correct']
        answer = quiz.models.UserAnswer(
            user=request.user,
            question=(
                quiz.models.Question.objects.filter(pk=self.kwargs['pk'])[0]
            ),
            is_correct=is_correct,
        )
        answer.save()
        return django.shortcuts.redirect(
            'quiz:user_answers_list', quiz_id=self.kwargs['quiz_id']
        )


class UserAnswersList(django.views.generic.ListView):
    """`мои посылки`"""

    template_name = 'quiz/user_answers_list.html'
    context_object_name = 'answers'
    paginate_by = 40

    def get_queryset(self, *args, **kwargs) -> django.db.models.QuerySet:
        """получаем queryset"""
        useful_answer_fields = (
            quiz.models.UserAnswer.objects.get_only_useful_list_fields()
            .filter(
                question__quiz__id=self.kwargs['quiz_id'],
                user__id=self.request.user.id,
            )
            .order_by('-time_answered')
        )
        return useful_answer_fields

    def get_context_data(self, *args, **kwargs) -> typing.Dict:
        """Дополняем контекст информацией об id викторины
        в которой сейчас участвуют"""
        context = super(UserAnswersList, self).get_context_data(
            *args, **kwargs
        )
        context['quiz_id'] = self.kwargs['quiz_id']
        return context


class StandingsList(django.views.generic.ListView):
    """`положение`"""

    template_name = 'quiz/user_answers_list.html'
    context_object_name = 'answers'
    paginate_by = 40

    def get_queryset(self, *args, **kwargs) -> django.db.models.QuerySet:
        """получаем queryset"""
        useful_answer_fields = (
            quiz.models.UserAnswer.objects.get_only_useful_list_fields()
            .filter(
                question__quiz__id=self.kwargs['quiz_id'],
            )
            .order_by('-time_answered')
        )
        return useful_answer_fields

    def get_context_data(self, *args, **kwargs) -> typing.Dict:
        """Дополняем контекст информацией об id викторины
        в которой сейчас участвуют"""
        context = super(StandingsList, self).get_context_data(*args, **kwargs)
        context['quiz_id'] = self.kwargs['quiz_id']
        return context

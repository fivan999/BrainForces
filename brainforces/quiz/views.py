import typing

import django.db.models
import django.http
import django.shortcuts
import django.views.generic

import quiz.forms
import quiz.models


class QuizMixinView(django.views.generic.View):
    """дополняем контекст именем организации и проверяем доступ пользователя"""

    def get_context_data(self, *args, **kwargs) -> dict:
        context = super().get_context_data(*args, **kwargs)
        organization_obj = (
            quiz.models.Organization.objects.filter_user_access(
                user_pk=self.request.user.pk,
            )
            .only('name')
            .first()
        )
        context['organization'] = organization_obj
        return context


class QuizDetailView(django.views.generic.DetailView):
    """детальная информация о викторине"""

    queryset = quiz.models.Quiz.objects.get_only_useful_list_fields()
    template_name = 'quiz/quiz_detail.html'
    context_object_name = 'quiz'


class QuestionsView(django.views.generic.ListView):
    """список вопросов в викторине"""

    template_name = 'quiz/questions.html'
    context_object_name = 'questions'

    def get_queryset(self) -> django.db.models.QuerySet:
        return quiz.models.Question.objects.filter(
            quiz__pk=self.kwargs['pk']
        ).prefetch_related(
            django.db.models.Prefetch(
                'useranswer_question',
                queryset=quiz.models.UserAnswer.objects.filter(
                    user__id=self.request.user.id
                ),
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
        context = super().get_context_data(*args, **kwargs)
        variants = quiz.models.Variant.objects.filter(
            question__id=self.kwargs['pk']
        )
        form = quiz.forms.AnswerForm()
        form.fields['answers'].choices = [
            (variant.id, variant.text) for variant in variants
        ]
        context['form'] = form
        return context

    def post(
        self, request: django.http.HttpRequest, pk: int, question_pk: int
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
                quiz.models.Question.objects.filter(pk=pk)[0]
            ),
            is_correct=is_correct,
        )
        answer.save()
        return django.shortcuts.redirect(
            'quiz:user_answers_list', pk=pk
        )


class UserAnswersList(django.views.generic.ListView):
    """`мои посылки`"""

    template_name = 'quiz/user_answers_list.html'
    context_object_name = 'answers'
    paginate_by = 40

    def get_queryset(self) -> django.db.models.QuerySet:
        """получаем queryset"""
        useful_answer_fields = (
            quiz.models.UserAnswer.objects.get_only_useful_list_fields()
            .filter(
                question__quiz__id=self.kwargs['quiz_id'],
                user__id=self.request.user.id,
            )
            .order_by('-time_answered')
        )
        return list(useful_answer_fields)


class StandingsList(django.views.generic.ListView):
    """положение"""

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
        return list(useful_answer_fields)

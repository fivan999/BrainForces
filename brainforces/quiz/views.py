import typing

import django.contrib.messages
import django.db.models
import django.http
import django.shortcuts
import django.urls
import django.utils.timezone
import django.views.generic

import quiz.forms
import quiz.mixins
import quiz.models
import quiz.services


class QuizListView(django.views.generic.ListView):
    """список викторин на главной странице"""

    template_name = 'quiz/list.html'
    context_object_name = 'quizzes'
    paginate_by = 5
    queryset = list(
        quiz.models.Quiz.objects.get_only_useful_list_fields().filter(
            is_private=False
        )
    )


class QuizDetailView(django.views.generic.DetailView):
    """детальная информация о викторине"""

    queryset = quiz.models.Quiz.objects.get_only_useful_list_fields()
    template_name = 'quiz/quiz_detail.html'
    context_object_name = 'quiz'

    def get_context_data(self, *args, **kwargs) -> dict:
        """право доступа"""
        context = super().get_context_data(*args, **kwargs)
        quiz_obj = context['object']
        can_access_quiz = quiz.services.user_can_access_quiz(
            quiz_obj, self.request.user
        )
        if not can_access_quiz:
            raise django.http.Http404()
        context['can_participate'] = quiz.models.QuizResults.objects.filter(
            quiz__pk=self.kwargs['pk'], user__pk=self.request.user.pk
        ).exists()
        quiz_status = quiz_obj.get_quiz_status()
        context['quiz_status'] = quiz_status
        if quiz_status == 1:
            context['can_access_questions'] = False
        elif quiz_status == 2:
            context['can_access_questions'] = context['can_participate']
        else:
            context[
                'can_access_questions'
            ] = quiz.services.user_can_access_quiz(quiz_obj, self.request.user)
        context['can_end'] = (
            quiz_status == 3 and quiz_obj.creator.pk == self.request.user.pk
        )
        context['now_time'] = str(django.utils.timezone.now())
        context['end_time'] = str(
            quiz_obj.start_time
            + django.utils.timezone.timedelta(minutes=quiz_obj.duration)
        )
        return context


class MakeQuizResultsView(django.views.generic.View):
    """администратор подводит итоги викторины"""

    def get(
        self, request: django.http.HttpRequest, pk: int
    ) -> django.http.HttpResponse:
        print(True)
        quiz_obj = django.shortcuts.get_object_or_404(
            quiz.models.Quiz, pk=pk, is_ended=False
        )
        if quiz_obj.creator.pk != request.user.pk:
            raise django.http.Http404()
        quiz.services.make_quiz_results(quiz_obj)
        django.contrib.messages.success(request, 'Успешно!')
        return django.shortcuts.redirect(
            django.urls.reverse('quiz:quiz_detail', kwargs={'pk': pk}),
        )


class QuestionsView(
    quiz.mixins.AccessToQuizMixin, django.views.generic.ListView
):
    """список вопросов в викторине"""

    template_name = 'quiz/questions.html'
    context_object_name = 'questions'

    def get_queryset(self) -> django.db.models.QuerySet:
        return (
            quiz.models.Question.objects.filter(quiz__pk=self.kwargs['pk'])
            .annotate(
                total_answers=django.db.models.Count(
                    'answers__id',
                    filter=django.db.models.Q(
                        answers__user__pk=self.request.user.pk
                    ),
                ),
                success_answers=django.db.models.Count(
                    'answers__id',
                    filter=django.db.models.Q(
                        answers__is_correct=True,
                        answers__user__pk=self.request.user.pk,
                    ),
                ),
            )
            .only('name')
        )


class QuestionDetailView(
    quiz.mixins.AccessToQuizMixin, django.views.generic.DetailView
):
    """детальная информация о вопросе"""

    template_name = 'quiz/question_detail.html'
    context_object_name = 'question'
    queryset = quiz.models.Question.objects.only('name', 'text', 'difficulty')
    pk_url_kwarg = 'question_pk'

    def get_context_data(self, *args, **kwargs) -> typing.Dict:
        """варианты ответа"""
        context = super().get_context_data(*args, **kwargs)
        variants = quiz.models.Variant.objects.filter(
            question__id=self.kwargs['question_pk']
        ).only('text')
        form = quiz.forms.AnswerForm()
        form.fields['answer'].choices = [
            (variant.id, variant.text) for variant in variants
        ]
        context['form'] = form
        return context

    def post(
        self, request: django.http.HttpRequest, pk: int, question_pk: int
    ) -> django.http.HttpResponse:
        """сохраняем ответ пользователя"""
        quiz_obj = django.shortcuts.get_object_or_404(quiz.models.Quiz, pk=pk)
        if quiz.services.user_can_access_quiz(quiz_obj, request.user):
            is_correct = quiz.models.Variant.objects.filter(
                pk=request.POST['answer'], is_correct=True
            ).exists()
            question_obj = quiz.models.Question.objects.get(pk=question_pk)
            quiz.models.UserAnswer.objects.create(
                user=request.user,
                question=question_obj,
                is_correct=is_correct,
            )
            quiz_result = quiz.models.QuizResults.objects.filter(
                quiz__pk=pk, user__pk=request.user.pk
            ).first()
            if (
                quiz_obj.get_quiz_status() == 2
                and quiz_result
                and is_correct
                and quiz.models.UserAnswer.objects.filter(
                    user__pk=request.user.pk,
                    question__pk=question_pk,
                    is_correct=is_correct,
                ).count()
                == 1
            ):
                quiz_result.solved += 1
                if quiz_obj.is_rated and not quiz_obj.is_private:
                    quiz_result.rating_after += question_obj.difficulty
                quiz_result.save()
        return django.shortcuts.redirect('quiz:user_answers_list', pk=pk)


class UserAnswersList(
    quiz.mixins.AccessToQuizMixin, django.views.generic.ListView
):
    """`мои посылки`"""

    template_name = 'quiz/user_answers_list.html'
    context_object_name = 'answers'
    paginate_by = 40

    def get_queryset(self) -> django.db.models.QuerySet:
        """получаем queryset"""
        useful_answer_fields = (
            quiz.models.UserAnswer.objects.get_only_useful_list_fields()
            .filter(
                question__quiz__id=self.kwargs['pk'],
                user__id=self.request.user.id,
            )
            .order_by('-time_answered')
        )
        return useful_answer_fields


class StandingsList(
    quiz.mixins.AccessToQuizMixin, django.views.generic.ListView
):
    """положение"""

    template_name = 'quiz/standing.html'
    context_object_name = 'results'
    paginate_by = 40

    def get_queryset(self, *args, **kwargs) -> django.db.models.QuerySet:
        """получаем queryset"""
        return (
            quiz.models.QuizResults.objects.select_related('user')
            .filter(quiz__pk=self.kwargs['pk'])
            .only('solved', 'user__username')
            .order_by('-solved')
        )


class QuizRegistrationView(django.views.generic.View):
    """регистрация на викторину"""

    def get(
        self, request: django.http.HttpRequest, pk: int
    ) -> django.http.HttpResponse:
        """регистрируем пользователя на викторину"""
        quiz_obj = django.shortcuts.get_object_or_404(quiz.models.Quiz, pk=pk)
        if (
            quiz.services.user_can_access_quiz(quiz_obj, request.user)
            and not quiz.models.QuizResults.objects.filter(
                quiz__pk=pk, user__pk=request.user.pk
            ).exists()
        ):
            quiz.models.QuizResults.objects.create(
                quiz=quiz_obj,
                user=request.user,
                rating_before=request.user.profile.rating,
                rating_after=request.user.profile.rating,
            )
            django.contrib.messages.success(request, 'Регистрация успешна!')
            return django.shortcuts.redirect(
                django.urls.reverse('quiz:quiz_detail', kwargs={'pk': pk})
            )
        else:
            raise django.http.Http404()

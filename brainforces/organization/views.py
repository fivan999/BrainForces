import django.contrib.auth.mixins
import django.contrib.messages
import django.db.models
import django.forms
import django.http
import django.shortcuts
import django.urls
import django.views.generic

import organization.forms
import organization.mixins
import organization.models
import quiz.forms
import quiz.models


class OrganizationMainView(django.views.generic.DetailView):
    """главная страница организации"""

    template_name = 'organization/profile.html'
    context_object_name = 'organization'

    def get_queryset(self) -> django.db.models.QuerySet:
        return organization.models.Organization.objects.filter_user_access(
            user_pk=self.request.user.pk
        ).only('name', 'description')

    def get_context_data(self, *args, **kwargs) -> dict:
        """дополняем контекст"""
        context = super().get_context_data(*args, **kwargs)
        org_user_manager = organization.models.OrganizationToUser.objects
        user = (
            org_user_manager.get_organization_member(
                pk=self.kwargs['pk'], user_pk=self.request.user.pk
            )
            .only('role')
            .first()
        )
        context['is_group_member'] = user is not None
        context['user_is_admin'] = context[
            'is_group_member'
        ] and user.role in (2, 3)
        return context


class OrganizationListView(django.views.generic.ListView):
    """список организаций"""

    template_name = 'organization/list.html'
    paginate_by = 5
    context_object_name = 'organizations'

    def get_queryset(self) -> django.db.models.QuerySet:
        return (
            organization.models.Organization.objects.filter(
                is_private=False
            )
            .only('name', 'description')
            .annotate(count_users=django.db.models.Count('users__id'))
            .order_by('-count_users')
        )


class OrganizationUsersView(
    organization.mixins.UserIsOrganizationMemberMixin,
    django.views.generic.ListView,
):
    """страница с пользователями организации"""

    template_name = 'organization/users.html'
    context_object_name = 'users'
    paginate_by = 50

    def get_queryset(self) -> django.db.models.QuerySet:
        return (
            organization.models.OrganizationToUser.objects.filter(
                organization__pk=self.kwargs['pk']
            )
            .select_related('user')
            .only('user__username', 'role')
        )

    def get_context_data(self, *args, **kwargs) -> dict:
        """дополняем контекст"""
        context = super().get_context_data(*args, **kwargs)
        if context['user_is_admin']:
            context['form'] = organization.forms.InviteToOrganizationForm()
        return context

    def post(
        self, request: django.http.HttpRequest, pk: int
    ) -> django.http.HttpResponsePermanentRedirect:
        """приглашаем пользователя в организацию"""
        form = organization.forms.InviteToOrganizationForm(
            request.POST or None
        )
        if form.is_valid():
            org_obj = django.shortcuts.get_object_or_404(
                organization.models.Organization,
                pk=pk,
            )

            invitation_allowed = (
                organization.models.OrganizationToUser.objects.filter(
                    user__pk=request.user.pk,
                    organization__pk=org_obj.pk,
                    role__in=(2, 3),
                )
            ).exists()

            if invitation_allowed:
                organization.models.OrganizationToUser.objects.create(
                    user=form.cleaned_data['user_obj'],
                    role=0,
                    organization=org_obj,
                )
                django.contrib.messages.success(
                    request, 'Приглашение отправлено'
                )
            else:
                raise django.http.Http404()
        else:
            django.contrib.messages.error(request, 'Ошибка')
        return django.shortcuts.redirect(
            django.urls.reverse('organization:users', kwargs={'pk': pk})
        )


class OrganizationQuizzesView(
    organization.mixins.UserIsOrganizationMemberMixin,
    django.views.generic.ListView,
):
    """список соревнований организации"""

    template_name = 'organization/quizzes.html'
    context_object_name = 'quizzes'
    paginate_by = 5

    def get_queryset(self) -> django.db.models.QuerySet:
        return quiz.models.Quiz.objects.get_only_useful_list_fields().filter(
            django.db.models.Q(is_private=False)
            | django.db.models.Q(
                organized_by__users__user__pk=self.request.user.pk
            ),
            organized_by__pk=self.kwargs['pk'],
        ).distinct()


class ActionWithUserView(django.views.generic.View):
    """
    получаем модель organizationtouser
    того кто спрашивает
    и того о ком спрашивают
    """

    def get(
        self, request: django.http.HttpRequest, pk: int, user_pk: int
    ) -> None:
        self.self_user = (
            organization.models.OrganizationToUser.objects.filter(
                organization__pk=pk,
                user__pk=request.user.pk,
            )
            .only('role')
            .first()
        )
        self.target_user = (
            organization.models.OrganizationToUser.objects.filter(
                user__pk=user_pk, organization__pk=pk
            )
            .only('role')
            .first()
        )


class DeleteUserFromOrganizationView(ActionWithUserView):
    """удаляем пользователя из организации"""

    def get(
        self, request: django.http.HttpRequest, pk: int, user_pk: int
    ) -> django.http.HttpResponsePermanentRedirect:
        super().get(request, pk, user_pk)
        if (
            self.self_user
            and self.target_user
            and (
                self.self_user.role > self.target_user.role
                or self.request.user.pk == user_pk
            )
        ):
            self.target_user.delete()
            django.contrib.messages.success(request, 'Успешно')
        else:
            django.contrib.messages.error(request, 'Ошибка')
        return django.shortcuts.redirect(
            django.urls.reverse('organization:users', kwargs={'pk': pk})
        )


class UpdateUserOrganizationRoleView(ActionWithUserView):
    """изменение статуса пользователя"""

    def get(
        self,
        request: django.http.HttpRequest,
        pk: int,
        user_pk: int,
        new_role: int,
    ) -> django.http.HttpResponsePermanentRedirect:
        super().get(request, pk, user_pk)
        if (
            self.self_user
            and self.target_user
            and (
                self.self_user.role > self.target_user.role
                or self.request.user.pk == user_pk
                and new_role == 1
            )
        ):
            self.target_user.role = new_role
            self.target_user.save()
            django.contrib.messages.success(request, 'Успешно')
        else:
            django.contrib.messages.error(request, 'Ошибка')
        return django.shortcuts.redirect(
            django.urls.reverse('organization:users', kwargs={'pk': pk})
        )


class OrganizationPostsView(
    organization.mixins.UserIsOrganizationMemberMixin,
    django.views.generic.ListView,
):
    """объявления организации"""

    template_name = 'organization/posts.html'
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self) -> django.db.models.QuerySet:
        return (
            organization.models.OrganizationPost.objects.filter_user_access(
                self.request.user.pk, org_pk=self.kwargs['pk']
            )
            .select_related('posted_by')
            .only('name', 'text', 'posted_by__id')
        )


class PostCommentsView(
    django.contrib.auth.mixins.LoginRequiredMixin,
    django.views.generic.ListView,
):
    """комментарии к посту"""

    template_name = 'organization/post_comments.html'
    paginate_by = 50
    context_object_name = 'comments'

    def get_context_data(self, *args, **kwargs) -> dict:
        """дополняем контекст"""
        context = super().get_context_data(*args, **kwargs)
        context['post'] = django.shortcuts.get_object_or_404(
            organization.models.OrganizationPost.objects.filter_user_access(
                self.request.user.pk, org_pk=self.kwargs['pk']
            ),
            pk=self.kwargs['post_pk'],
        )
        return context

    def get_queryset(self) -> django.db.models.QuerySet:
        return (
            organization.models.CommentToOrganizationPost.objects.filter(
                post__pk=self.kwargs['post_pk']
            )
            .select_related('user')
            .only('user__username', 'text')
        )

    def post(
        self, request: django.http.HttpResponse, pk: int, post_pk: int
    ) -> django.http.HttpResponsePermanentRedirect:
        """обрабатываем добавление комментария"""
        comment_text = request.POST.get('comment_text')
        post = django.shortcuts.get_object_or_404(
            organization.models.OrganizationPost.objects.filter_user_access(
                self.request.user.pk, org_pk=self.kwargs['pk']
            ),
            pk=self.kwargs['post_pk'],
        )
        if comment_text:
            organization.models.CommentToOrganizationPost.objects.create(
                user=request.user, text=comment_text, post=post
            )
        return django.shortcuts.redirect(
            django.urls.reverse(
                'organization:post_detail',
                kwargs={'pk': pk, 'post_pk': post_pk},
            )
        )


class ChooseQuizQuestionsNumber(
    organization.mixins.UserIsOrganizationMemberMixin,
    django.views.generic.edit.FormView,
):
    """выбор количества вопросов в викторине"""

    template_name = 'organization/choose_questions_num.html'
    form_class = quiz.forms.QuizQuestionsNumberForm

    def get_context_data(self, *args, **kwargs) -> dict:
        """проверка на админа"""
        context = super().get_context_data(*args, **kwargs)
        if not context['user_is_admin']:
            raise django.http.Http404()
        return context

    def form_valid(
        self, form: quiz.forms.QuizQuestionsNumberForm
    ) -> django.http.HttpResponse:
        """редиректим на создание викторины"""
        return django.shortcuts.redirect(
            django.urls.reverse(
                'organization:create_quiz',
                kwargs={
                    'pk': self.kwargs['pk'],
                    'num_questions': form.cleaned_data['num_questions'],
                },
            )
        )


class QuizCreateView(
    organization.mixins.UserIsOrganizationMemberMixin,
    django.views.generic.edit.FormView,
):
    """создание викторины"""

    template_name = 'organization/create_quiz.html'
    form_class = quiz.forms.QuizForm

    def get_context_data(self, *args, **kwargs) -> dict:
        """дополняем контекст формсетом и проверкой на права доступа"""
        context = super().get_context_data(*args, **kwargs)
        if not context['user_is_admin']:
            raise django.http.Http404()
        question_formset = django.forms.inlineformset_factory(
            quiz.models.Quiz,
            quiz.models.Question,
            form=quiz.forms.QuestionForm,
            extra=self.kwargs['num_questions'],
        )
        context['question_formset'] = question_formset()
        return context

    def post(
        self, request: django.http.HttpRequest, pk: int, num_questions: int
    ) -> django.http.HttpResponse:
        """обрабатываем создание викторины"""
        context = self.get_context_data()
        quiz_form = self.form_class(request.POST or None)
        question_formset = django.forms.inlineformset_factory(
            quiz.models.Quiz,
            quiz.models.Question,
            form=quiz.forms.QuestionForm,
            extra=self.kwargs['num_questions'],
        )(self.request.POST or None)
        if quiz_form.is_valid():
            quiz_obj = quiz_form.save(commit=False)
            quiz_obj.organized_by = (
                organization.models.Organization.objects.get(
                    pk=self.kwargs['pk']
                )
            )
            quiz_obj.creator = request.user
            question_objects = list()
            variants_objects = list()
            formset_valid = True
            for question in question_formset:
                if question.is_valid():
                    question_obj = question.save(commit=False)
                    question_obj.quiz = quiz_obj
                    question_objects.append(question_obj)
                    variants = question.cleaned_data['variants']
                    for variant in variants:
                        if variant.endswith('right'):
                            variant_obj = quiz.models.Variant(
                                text=variant[: variant.rfind('right')],
                                question=question_obj,
                                is_correct=True,
                            )
                        else:
                            variant_obj = quiz.models.Variant(
                                text=variant,
                                question=question_obj,
                                is_correct=False,
                            )
                        variants_objects.append(variant_obj)
                else:
                    formset_valid = False
            if formset_valid:
                quiz_obj.save()
                for item in question_objects + variants_objects:
                    item.save()
                return django.shortcuts.redirect(
                    django.urls.reverse(
                        'organization:quizzes', kwargs={'pk': pk}
                    )
                )
        context['question_formset'] = question_formset
        context['form'] = quiz_form
        return django.shortcuts.render(request, self.template_name, context)


class CreatePostView(
    organization.mixins.UserIsOrganizationMemberMixin,
    django.views.generic.edit.FormView,
):
    """создание публикации организации"""

    form_class = organization.forms.PostForm
    template_name = 'organization/create_post.html'

    def get_context_data(self, *args, **kwargs) -> dict:
        context = super().get_context_data(*args, **kwargs)
        if not context['user_is_admin']:
            raise django.http.Http404()
        return context

    def post(
        self, request: django.http.HttpRequest, pk: int
    ) -> django.http.HttpResponse:
        """обрабатываем форму"""
        if not organization.models.OrganizationToUser.objects.filter(
            user__pk=self.request.user.pk, organization__pk=pk, role__in=(2, 3)
        ).exists():
            raise django.http.Http404()
        form = self.form_class(request.POST or None)
        if form.is_valid():
            post_obj = form.save(commit=False)
            post_obj.posted_by = organization.models.Organization.objects.get(
                pk=pk
            )
            post_obj.save()
            return django.shortcuts.redirect(self.get_success_url())
        return django.shortcuts.render(
            request, self.template_name, {'form': form}
        )

    def get_success_url(self) -> str:
        """редиректим при успешной отправке формы"""
        return django.urls.reverse_lazy(
            'organization:posts', kwargs={'pk': self.kwargs['pk']}
        )

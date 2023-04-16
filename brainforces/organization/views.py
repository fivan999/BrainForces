import django.contrib.messages
import django.db.models
import django.http
import django.shortcuts
import django.urls
import django.views.generic

import organization.forms
import organization.models
import quiz.forms
import quiz.models


class OrganizationMixinView(django.views.generic.View):
    """дополняем контекст именем организации и проверяем доступ пользователя"""

    def get_context_data(self, *args, **kwargs) -> dict:
        context = super().get_context_data(*args, **kwargs)
        organization_obj = (
            organization.models.Organization.objects.filter_user_access(
                user_pk=self.request.user.pk
            )
            .only('name')
            .first()
        )
        context['organization'] = organization_obj
        return context


class UserIsOrganizationMemberMixinView(OrganizationMixinView):
    """пользователь - участник организации"""

    def get_context_data(self, *args, **kwargs) -> dict:
        context = super().get_context_data(*args, **kwargs)
        org_user_obj = organization.models.OrganizationToUser.objects.filter(
            user__pk=self.request.user.pk, organization__pk=self.kwargs['pk']
        ).first()
        context['organization_to_user'] = org_user_obj
        context['is_group_member'] = org_user_obj is not None
        context['user_is_admin'] = (
            org_user_obj.role in (2, 3)
            if context['is_group_member']
            else False
        )
        return context


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
                org_pk=self.kwargs['pk'], user_pk=self.request.user.pk
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
        return list(
            organization.models.Organization.objects.filter_user_access(
                user_pk=self.request.user.pk
            )
            .only('name', 'description')
            .annotate(count_users=django.db.models.Count('users__id'))
            .order_by('-count_users')
        )


class OrganizationUsersView(
    UserIsOrganizationMemberMixinView, django.views.generic.ListView
):
    """страница с пользователями организации"""

    template_name = 'organization/users.html'
    context_object_name = 'users'
    paginate_by = 50

    def get_queryset(self) -> django.db.models.QuerySet:
        return list(
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
            invited_user = form.cleaned_data['user_obj']

            invitation_allowed = (
                organization.models.OrganizationToUser.objects.filter(
                    user__pk=request.user.pk,
                    organization__pk=org_obj.pk,
                    role__in=(2, 3),
                )
            ).exists()

            if invitation_allowed:
                try:
                    organization.models.OrganizationToUser.objects.create(
                        user=invited_user, role=0, organization=org_obj
                    )
                    django.contrib.messages.success(
                        request, 'Приглашение отправлено'
                    )
                except Exception:
                    django.contrib.messages.error(request, 'Ошибка')
            else:
                django.contrib.messages.error(request, 'Ошибка')
        else:
            django.contrib.messages.error(request, 'Ошибка')
        return django.shortcuts.redirect(
            django.urls.reverse('organization:users', kwargs={'pk': pk})
        )


class OrganizationQuizzesView(
    UserIsOrganizationMemberMixinView, django.views.generic.ListView
):
    """список соревнований организации"""

    template_name = 'organization/quizzes.html'
    context_object_name = 'quizzes'
    paginate_by = 5

    def get_queryset(self) -> django.db.models.QuerySet:
        return list(
            quiz.models.Quiz.objects.get_only_useful_list_fields().filter(
                django.db.models.Q(is_private=False)
                | django.db.models.Q(
                    organized_by__users__user__pk=self.request.user.pk
                ),
                organized_by__pk=self.kwargs['pk']
            )
        )


class ActionWithUserView(django.views.generic.View):
    def get(
        self, request: django.http.HttpRequest, org_pk: int, user_pk: int
    ) -> None:
        self.self_user = (
            organization.models.OrganizationToUser.objects.filter(
                organization__pk=org_pk,
                user__pk=request.user.pk,
            )
            .only('role')
            .first()
        )
        self.target_user = (
            organization.models.OrganizationToUser.objects.filter(
                user__pk=user_pk, organization__pk=org_pk
            )
            .only('role')
            .first()
        )


class DeleteUserFromOrganizationView(ActionWithUserView):
    """удаляем пользователя из организации"""

    def get(
        self, request: django.http.HttpRequest, org_pk: int, user_pk: int
    ) -> django.http.HttpResponsePermanentRedirect:
        super().get(request, org_pk, user_pk)
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
            django.urls.reverse('organization:users', kwargs={'pk': org_pk})
        )


class UpdateUserOrganizationRoleView(ActionWithUserView):
    """изменение статуса пользователя"""

    def get(
        self,
        request: django.http.HttpRequest,
        org_pk: int,
        user_pk: int,
        new_role: int,
    ) -> django.http.HttpResponsePermanentRedirect:
        super().get(request, org_pk, user_pk)
        print(self.self_user, self.target_user)
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
            django.urls.reverse('organization:users', kwargs={'pk': org_pk})
        )


class OrganizationPostsView(
    UserIsOrganizationMemberMixinView, django.views.generic.ListView
):
    """объявления организации"""

    template_name = 'organization/posts.html'
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self) -> django.db.models.QuerySet:
        return list(
            organization.models.OrganizationPost.objects.filter(
                posted_by__pk=self.kwargs['pk']
            )
            .select_related('posted_by')
            .only('name', 'text', 'posted_by__id')
        )


class PostCommentsView(
    UserIsOrganizationMemberMixinView, django.views.generic.ListView
):
    """комментарии к посту"""

    template_name = 'organization/post_comments.html'
    paginate_by = 50
    context_object_name = 'comments'

    def get_context_data(self, *args, **kwargs) -> dict:
        """дополняем контекст"""
        context = super().get_context_data(*args, **kwargs)
        if not context['is_group_member']:
            raise django.http.Http404()
        context['post'] = django.shortcuts.get_object_or_404(
            organization.models.OrganizationPost, pk=self.kwargs['post_pk']
        )
        return context

    def get_queryset(self) -> django.db.models.QuerySet:
        return list(
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
            organization.models.OrganizationPost, pk=post_pk, posted_by__pk=pk
        )
        django.shortcuts.get_object_or_404(
            organization.models.OrganizationToUser,
            organization__pk=pk,
            user__pk=request.user.pk,
            role__in=(1, 2, 3),
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


class QuizCreateView(django.views.generic.View):
    """создание викторины"""

    def get(
        self, request: django.http.HttpRequest, pk: int
    ) -> django.http.HttpResponse:
        if not organization.models.OrganizationToUser.objects.filter(
            user__pk=self.request.user.pk, organization__pk=pk, role__in=(2, 3)
        ).exists():
            raise django.http.Http404()
        context = {
            'quiz_form': quiz.forms.QuizForm(),
            'question_formset': quiz.forms.QuestionFormSet(),
            'variant_formset': quiz.forms.VariantFormSet(),
            'user_is_admin': True
        }
        return django.shortcuts.render(
            request, 'organization/create_quiz.html', context
        )

    def post(
        self, request: django.http.HttpRequest, pk: int
    ) -> django.http.HttpResponse:
        if not organization.models.OrganizationToUser.objects.filter(
            user__pk=self.request.user.pk, organization__pk=pk, role__in=(2, 3)
        ).exists():
            raise django.http.Http404()
        quiz_form = quiz.forms.QuizForm(request.POST or None)
        question_formset = quiz.forms.QuestionFormSet(request.POST or None)
        variant_formset = quiz.forms.VariantFormSet(request.POST or None)
        if (
            quiz_form.is_valid()
            and question_formset.is_valid()
            and variant_formset.is_valid()
        ):
            quiz_obj = quiz_form.save(commit=False)
            quiz_obj.organized_by = (
                organization.models.Organization.objects.get(pk=pk)
            )
            quiz_obj.creator = request.user
            quiz_obj.save()
            questions = question_formset.save(commit=False)
            for question in questions:
                question.quiz = quiz_obj
                question.save()
            variants = variant_formset.save(commit=False)
            for variant in variants:
                variant.question = question
                variant.save()
            return django.shortcuts.redirect(
                django.urls.reverse('organization:quizzes', kwargs={'pk': pk})
            )
        context = {
            'quiz_form': quiz_form,
            'question_formset': question_formset,
            'variant_formset': variant_formset,
        }
        return django.shortcuts.render(
            request, 'organization/create_quiz.html', context
        )


# class CreatePostView(
#     UserIsOrganizationMemberMixinView, django.views.generic.edit.FormView
# ):
#     """создание публикации организации"""

#     form_class = organization.forms.PostForm
#     template_name = 'organization/create_post.html'

#     def post(self, request: django.http.HttpRequest, pk: int) -> django.http.HttpResponse:
#         """обрабатываем форму"""
#         form = self.form_class(request.POST or None)
#         if form.is_valid():
#             post_obj = form.save(commit=False)
#             post_obj.posted_by =
#             return redirect(self.success_url)
#         return render(request, self.template_name, {'form': form})

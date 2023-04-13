import django.contrib.messages
import django.db.models
import django.http
import django.shortcuts
import django.urls
import django.views.generic

import organization.forms
import organization.models
import quiz.models


class OrganizationNameMixinView(django.views.generic.View):
    """дополняем контекст именем организации"""

    def get_context_data(self, *args, **kwargs) -> dict:
        context = super().get_context_data(*args, **kwargs)
        organization_name = django.shortcuts.get_object_or_404(
            organization.models.Organization.objects.filter_user_access(
                user_pk=self.request.user.pk
            ).only('name'),
            pk=self.kwargs.get('pk'),
        ).name
        context['organization_name'] = organization_name
        return context


class OrganizationMainView(django.views.generic.DetailView):
    """главная страница организации"""

    template_name = 'organization/profile.html'
    context_object_name = 'organization'
    queryset = (
        organization.models.Organization.objects.get_only_useful_fields()
    )

    def get_context_data(self, *args, **kwargs) -> dict:
        """дополняем контекст"""
        context = super().get_context_data(*args, **kwargs)
        user = (
            organization.models.OrganizationToUser.objects.filter(
                organization__pk=self.kwargs['pk'],
                user__pk=self.request.user.pk,
                role__in=(1, 2, 3),
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
            organization.models.Organization.objects.filter_user_access(
                user_pk=self.request.user.pk
            )
            .only('name', 'description')
            .annotate(count_users=django.db.models.Count('users__id'))
            .order_by('-count_users')
        )


class OrganizationUsersView(
    OrganizationNameMixinView, django.views.generic.ListView
):
    """страница с пользователями организации"""

    template_name = 'organization/users.html'
    context_object_name = 'users'

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
        context['user_is_admin'] = (
            organization.models.OrganizationToUser.objects.filter(
                organization__pk=self.kwargs['pk'],
                user__pk=self.request.user.pk,
                role__in=(2, 3),
            )
        ).exists()
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
                        user=invited_user, role=4, organization=org_obj
                    )
                    django.contrib.messages.success(
                        request, 'Приглашение отправлено'
                    )
                except Exception:
                    django.contrib.messages.error(request, 'Ошибка')
            else:
                django.contrib.messages.error(request, 'Ошибка')
        return django.shortcuts.redirect(
            django.urls.reverse('organization:users', kwargs={'pk': pk})
        )


class OrganizationQuizzesView(
    OrganizationNameMixinView, django.views.generic.ListView
):
    """список соревнований организации"""

    template_name = 'organization/quizzes.html'
    context_object_name = 'quizzes'
    paginate_by = 5

    def get_queryset(self) -> django.db.models.QuerySet:
        return quiz.models.Quiz.objects.get_only_useful_list_fields().filter(
            organized_by=self.kwargs['pk']
        )


class DeleteUserFromOrganizationView(django.views.generic.View):
    """удаляем пользователя из организации"""

    def get(
        self, request: django.http.HttpRequest, org_pk: int, user_pk: int
    ) -> django.http.HttpResponsePermanentRedirect:
        if (
            request.user.pk == user_pk
            or organization.models.OrganizationToUser.objects.filter(
                organization__pk=org_pk,
                user__pk=request.user.pk,
                role__in=(2, 3),
            ).exists()
        ):
            organization.models.OrganizationToUser.objects.filter(
                user__pk=user_pk, organization__pk=org_pk
            ).delete()
            django.contrib.messages.success(request, 'Успешно')
        else:
            django.contrib.messages.error(request, 'Ошибка')
        return django.shortcuts.redirect(
            django.urls.reverse('organization:users', kwargs={'pk': org_pk})
        )


class UpdateUserOrganizationRoleView(django.views.generic.View):
    """изменение статуса пользователя"""

    def get(
        self,
        request: django.http.HttpRequest,
        org_pk: int,
        user_pk: int,
        new_role: int,
    ) -> django.http.HttpResponsePermanentRedirect:
        if (
            organization.models.OrganizationToUser.objects.filter(
                organization__pk=org_pk,
                user__pk=request.user.pk,
                role__in=(2, 3),
            ).exists()
            or request.user.pk == user_pk
            and new_role == 1
        ):
            organization.models.OrganizationToUser.objects.filter(
                user__pk=user_pk, organization__pk=org_pk
            ).update(role=new_role)
            django.contrib.messages.success(request, 'Успешно')
        else:
            django.contrib.messages.error(request, 'Ошибка')
        return django.shortcuts.redirect(
            django.urls.reverse('organization:users', kwargs={'pk': org_pk})
        )


class OrganizationPostsView(
    OrganizationNameMixinView, django.views.generic.ListView
):
    """объявления организации"""

    template_name = 'organization/posts.html'
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self) -> django.db.models.QuerySet:
        return (
            organization.models.OrganizationPost.objects.filter(
                posted_by__pk=self.kwargs['pk']
            )
            .select_related('posted_by')
            .only('name', 'text', 'posted_by__id')
        )


class PostCommentsView(
    OrganizationNameMixinView, django.views.generic.ListView
):
    """комментарии к посту"""

    template_name = 'organization/post_comments.html'
    paginate_by = 50
    context_object_name = 'comments'

    def get_context_data(self, *args, **kwargs) -> dict:
        """дополняем контекст"""
        context = super().get_context_data(*args, **kwargs)
        context['post'] = django.shortcuts.get_object_or_404(
            organization.models.OrganizationPost, pk=self.kwargs['post_pk']
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

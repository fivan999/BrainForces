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
            organization.models.Organization.objects.all().only('name'),
            pk=self.kwargs['pk'],
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
        context[
            'is_group_member'
        ] = organization.models.OrganizationToUser.objects.filter(
            organization__pk=self.kwargs['pk'], user__pk=self.request.user.pk
        ).exists()
        return context


class OrganizationListView(django.views.generic.ListView):
    """список организаций"""

    template_name = 'organization/list.html'
    paginate_by = 5
    context_object_name = 'organizations'

    def get_queryset(self) -> django.db.models.QuerySet:
        return (
            organization.models.Organization.objects.get_only_useful_fields()
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
                organization.models.Organization.objects.prefetch_related(
                    django.db.models.Prefetch(
                        'users',
                        queryset=(
                            organization.models.OrganizationToUser.objects
                            .select_related(
                                'user'
                            )
                        ),
                    )
                ),
                pk=pk,
            )
            invited_user = form.cleaned_data['user_obj']

            # нужно проверить, если пользователь отправивший запрос
            # является администратором группы
            # и приглашаемого пользователя нет в группе
            invitation_allowed, user_in_org = False, False
            for user in org_obj.users.all():
                if user.user.id == self.request.user.pk and user.role in (
                    2,
                    3,
                ):
                    invitation_allowed = True
                if user.user.id == invited_user.pk:
                    user_in_org = True
                    break

            if not user_in_org and invitation_allowed:
                organization.models.OrganizationToUser.objects.create(
                    user=invited_user, role=4, organization=org_obj
                )
                django.contrib.messages.success(
                    request, 'Приглашение отправлено'
                )
            else:
                django.contrib.messages.error(request, 'Недостаточно прав')
        return django.shortcuts.redirect(
            django.urls.reverse(
                'organization:organization_users', kwargs={'pk': pk}
            )
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
            django.contrib.messages.error(request, 'Недостаточно прав')
        return django.shortcuts.redirect(
            django.urls.reverse(
                'organization:organization_users', kwargs={'pk': org_pk}
            )
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
        if organization.models.OrganizationToUser.objects.filter(
            organization__pk=org_pk, user__pk=request.user.pk, role__in=(2, 3)
        ).exists():
            organization.models.OrganizationToUser.objects.filter(
                user__pk=user_pk, organization__pk=org_pk
            ).update(role=new_role)
            django.contrib.messages.success(request, 'Успешно')
        else:
            django.contrib.messages.error(request, 'Недостаточно прав')
        return django.shortcuts.redirect(
            django.urls.reverse(
                'organization:organization_users', kwargs={'pk': org_pk}
            )
        )

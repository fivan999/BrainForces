import organization.models

import django.db.models
import django.http
import django.shortcuts
import django.views.generic

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
        organization.models.Organization
        .objects.get_only_useful_detail_fields()
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
        return context


class OrganizationQuizzesView(
    OrganizationNameMixinView, django.views.generic.ListView
):
    """список соревнований организации"""

    template_name = 'organization/quizzes.html'
    context_object_name = 'quizzes'

    def get_queryset(self) -> django.db.models.QuerySet:
        return quiz.models.Quiz.objects.get_only_useful_list_fields().filter(
            organized_by=self.kwargs['pk']
        )

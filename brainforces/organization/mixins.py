import django.http
import django.views.generic

import organization.models


class OrganizationMixin(django.views.generic.View):
    """дополняем контекст именем организации и проверяем доступ пользователя"""

    def get_context_data(self, *args, **kwargs) -> dict:
        context = dict()
        if hasattr(super(), 'get_context_data'):
            context = super().get_context_data(*args, **kwargs)
        organization_obj = django.shortcuts.get_object_or_404(
            organization.models.Organization.objects.filter_user_access(
                user_pk=self.request.user.pk
            ).only('name', 'is_private'),
            pk=self.kwargs['pk'],
        )
        context['organization'] = organization_obj
        return context


class UserIsOrganizationMemberMixin(OrganizationMixin):
    """пользователь - участник организации"""

    def get_context_data(self, *args, **kwargs) -> dict:
        """
        добавляем в контекст переменные объекта organization_to_user,
        является ли пользователь участником группы
        и является ли он ее администратором
        """
        context = super().get_context_data(*args, **kwargs)
        org_user_manager = organization.models.OrganizationToUser.objects
        org_user_obj = org_user_manager.get_organization_member(
            org_pk=self.kwargs['pk'], user_pk=self.request.user.pk
        ).first()
        context['organization_to_user'] = org_user_obj
        context['is_group_member'] = org_user_obj is not None
        context['user_is_admin'] = (
            org_user_obj.role in (2, 3)
            if context['is_group_member']
            else False
        )
        return context


class IsAdminMixin(UserIsOrganizationMemberMixin):
    """
    к странице с этим миксином может получить доступ
    только админ организации
    """

    def get_context_data(self, *args, **kwargs) -> dict:
        context = super().get_context_data(*args, **kwargs)
        if not context['user_is_admin']:
            raise django.http.Http404()
        return context

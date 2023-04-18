import django.views.generic

import organization.models


class OrganizationMixin(django.views.generic.View):
    """дополняем контекст именем организации и проверяем доступ пользователя"""

    def get_context_data(self, *args, **kwargs) -> dict:
        context = super().get_context_data(*args, **kwargs)
        organization_obj = django.shortcuts.get_object_or_404(
            organization.models.Organization.objects.filter_user_access(
                user_pk=self.request.user.pk
            ).only('name'),
            pk=self.kwargs['pk'],
        )
        context['organization'] = organization_obj
        return context


class UserIsOrganizationMemberMixin(OrganizationMixin):
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

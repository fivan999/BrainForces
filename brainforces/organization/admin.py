import organization.models

import django.contrib.admin


@django.contrib.admin.register(organization.models.Organization)
class OrganizationAdmin(django.contrib.admin.ModelAdmin):
    """отображение модели Organization в админке"""

    list_display = ('id', 'name')
    list_display_links = ('id',)


@django.contrib.admin.register(organization.models.OrganizationToUser)
class OrganizationToUserAdmin(django.contrib.admin.ModelAdmin):
    """отображение модели OrganizationToUser"""

    list_display = ('id', 'user', 'organization', 'role')
    list_editable = ('role',)
    list_display_links = ('id',)

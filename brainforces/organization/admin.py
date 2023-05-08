import django.contrib.admin

import organization.models


@django.contrib.admin.register(organization.models.Organization)
class OrganizationAdmin(django.contrib.admin.ModelAdmin):
    """отображение модели Organization в админке"""

    list_display = ('id', 'name', 'is_private', 'is_active')
    list_display_links = ('id',)
    list_editable = ('is_private', 'is_active')
    list_filter = ('is_active',)


@django.contrib.admin.register(organization.models.OrganizationToUser)
class OrganizationToUserAdmin(django.contrib.admin.ModelAdmin):
    """отображение модели OrganizationToUser в админке"""

    list_display = ('id', 'user', 'organization', 'role')
    list_editable = ('role',)
    list_display_links = ('id',)


@django.contrib.admin.register(organization.models.OrganizationPost)
class OrganizationPostAdmin(django.contrib.admin.ModelAdmin):
    """отображение модели OrganizationPost в админке"""

    list_display = ('id', 'name', 'posted_by', 'is_private')
    list_display_links = ('id',)
    list_editable = ('is_private',)


@django.contrib.admin.register(organization.models.CommentToOrganizationPost)
class CommentToOrganizationPostAdmin(django.contrib.admin.ModelAdmin):
    """отображение модели CommentToOrganizationPost в админке"""

    list_display = ('id', 'user', 'post')
    list_display_links = ('id',)

import typing

import django.shortcuts

import organization.models


def get_post_by_user_organization_post_or_404(
    user_pk: int, org_pk: int, post_pk: int
) -> typing.Optional[organization.models.OrganizationPost]:
    """получаем объект поста по user_pk, org_pk и post_pk"""
    return django.shortcuts.get_object_or_404(
        organization.models.OrganizationPost.objects.filter_user_access(
            user_pk=user_pk, org_pk=org_pk
        ),
        pk=post_pk,
    )

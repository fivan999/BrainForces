import typing

import organization.models


def get_post_by_user_organization_post_or_404(
    user_pk: int, org_pk: int, post_pk: int
) -> typing.Optional[organization.models.OrganizationPost]:
    """получаем объект поста по user_pk, org_pk и post_pk"""
    return (
        organization.models.OrganizationPost.objects.filter_user_access(
            user_pk=user_pk, org_pk=org_pk
        )
        .filter(pk=post_pk)
        .first()
    )

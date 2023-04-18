import django.db.models


class OrganizationManager(django.db.models.Manager):
    """менеджер модели Organization"""

    def get_only_useful_fields(self) -> django.db.models.QuerySet:
        """только нужные поля для одной организации"""
        return self.get_queryset().only('name', 'description')

    def filter_user_access(self, user_pk: int) -> django.db.models.QuerySet:
        """доступ пользователя к группе"""
        return (
            self.get_queryset()
            .filter(
                django.db.models.Q(
                    is_private=True,
                    users__user__pk=user_pk,
                    users__role__in=(1, 2, 3),
                )
                | django.db.models.Q(is_private=False)
            )
            .distinct()
        )


class OrganizationPostManager(django.db.models.Manager):
    """менеджер модели OrganizationPost"""

    def get_only_useful_fields(self) -> django.db.models.QuerySet:
        """только нужные поля для поста"""
        return self.get_queryset().only('name', 'text')

    def filter_user_access(
        self, user_pk: int, org_pk: int = None
    ) -> django.db.models.QuerySet:
        """доступ пользователя к посту"""
        posts_queryset = self.get_queryset().filter(
            django.db.models.Q(posted_by__users__user__pk=user_pk)
            | django.db.models.Q(is_private=False)
        )
        if org_pk:
            posts_queryset.filter(posted_by__pk=org_pk)
        return posts_queryset.distinct()


class OrganizationToUserManager(django.db.models.Manager):
    """менеджер модели OrganizationToUSer"""

    def get_organization_member(self, pk: int, user_pk: int) -> bool:
        """пользователь - участник организации"""
        return self.get_queryset().filter(
            organization__pk=pk,
            user__pk=user_pk,
            role__in=(1, 2, 3),
        )

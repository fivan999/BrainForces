import django.db.models


class OrganizationManager(django.db.models.Manager):
    """менеджер модели Organization"""

    def get_active_organizations(self) -> django.db.models.QuerySet:
        """только активные организации"""
        return self.get_queryset().filter(is_active=True)

    def get_only_useful_fields(self) -> django.db.models.QuerySet:
        """только нужные поля для одной организации"""
        return self.get_active_organizations().only('name', 'description')

    def filter_user_access(self, user_pk: int) -> django.db.models.QuerySet:
        """
        доступ пользователя к группе
        либо группа не приватная,
        либо пользователь в ней состоит
        """
        return (
            self.get_only_useful_fields()
            .filter(
                django.db.models.Q(
                    users__user__pk=user_pk,
                    users__role__in=(1, 2, 3),
                )
                | django.db.models.Q(is_private=False)
            )
            .distinct()
        )


class OrganizationPostManager(django.db.models.Manager):
    """менеджер модели OrganizationPost"""

    def get_posts_with_active_organizations(self) -> django.db.models.QuerySet:
        """посты только активных организаций"""
        return self.get_queryset().filter(posted_by__is_active=True)

    def get_only_useful_fields(self) -> django.db.models.QuerySet:
        """только нужные поля для поста"""
        return (
            self.get_posts_with_active_organizations()
            .select_related('posted_by')
            .only('name', 'text', 'posted_by__name')
        )

    def filter_user_access(
        self, user_pk: int, org_pk: int = -1
    ) -> django.db.models.QuerySet:
        """
        доступ пользователя к посту
        либо оргация не приватная,
        либо пользователь ее участник
        """
        posts_queryset = self.get_only_useful_fields().filter(
            django.db.models.Q(posted_by__is_private=False)
            & django.db.models.Q(is_private=False)
            | django.db.models.Q(posted_by__users__user__pk=user_pk)
        )
        if org_pk != -1:
            posts_queryset = posts_queryset.filter(posted_by__pk=org_pk)
        return posts_queryset.distinct()


class OrganizationToUserManager(django.db.models.Manager):
    """менеджер модели OrganizationToUSer"""

    def get_active_organization_to_user(self) -> django.db.models.QuerySet:
        """только с активными огранизациями"""
        return self.get_queryset().filter(organization__is_active=True)

    def get_organization_member(
        self, org_pk: int, user_pk: int
    ) -> django.db.models.QuerySet:
        """пользователь - участник организации"""
        return self.get_queryset().filter(
            organization__pk=org_pk,
            user__pk=user_pk,
            role__in=(1, 2, 3),
            organization__is_active=True,
        )

    def get_organization_admin(
        self, org_pk: int, user_pk: int
    ) -> django.db.models.QuerySet:
        """пользователь - админ организации"""
        return self.get_organization_member(org_pk, user_pk).filter(
            role__in=(2, 3)
        )

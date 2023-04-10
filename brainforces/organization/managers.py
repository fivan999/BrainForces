import django.db.models


class OrganizationManager(django.db.models.Manager):
    """менеджер модели Organization"""

    def get_only_useful_detail_fields(self) -> django.db.models.QuerySet:
        """только нужные поля для одной организации"""
        return self.get_queryset().only('name', 'description')

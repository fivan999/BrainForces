import ckeditor_uploader.fields

import django.db.models
import django.urls

import organization.managers
import users.models


class Organization(django.db.models.Model):
    """модель организации"""

    objects = organization.managers.OrganizationManager()

    name = django.db.models.CharField(
        verbose_name='название',
        help_text='Название организации',
        max_length=100,
    )

    description = ckeditor_uploader.fields.RichTextUploadingField(
        verbose_name='описание', help_text='Описание организации'
    )

    class Meta:
        verbose_name = 'организация'
        verbose_name_plural = 'организации'

    def __str__(self) -> str:
        """строковое представление"""
        return self.name[:20]

    def get_absolute_url(self):
        """путь к organization detail"""
        return django.urls.reverse_lazy(
            'organization:profile', kwargs={'pk': self.pk}
        )


class OrganizationToUser(django.db.models.Model):
    """связь организации с пользователем"""

    class UserRoles(django.db.models.IntegerChoices):
        """роли пользователя в органицазии"""

        PARTICIPANT = 1, 'Участник'
        ADMIN = 2, 'Админ'
        CREATOR = 3, 'Создатель'
        INVITED = 4, 'Приглашен'

    organization = django.db.models.ForeignKey(
        Organization,
        verbose_name='организация',
        help_text='Организация, в которой состоит пользователь',
        on_delete=django.db.models.CASCADE,
        related_name='users',
    )

    user = django.db.models.ForeignKey(
        users.models.User,
        verbose_name='пользователь',
        help_text='Пользователь, состоящий в организации',
        on_delete=django.db.models.CASCADE,
        related_name='organizations',
    )

    role = django.db.models.IntegerField(
        choices=UserRoles.choices,
        verbose_name='роль',
        help_text='Роль пользователя в организации',
        default=1,
    )

    class Meta:
        unique_together = ('user', 'organization')
        verbose_name = 'участник'
        verbose_name_plural = 'участники'

    def __str__(self) -> str:
        """строковое представление"""
        return f'Участник организации {self.pk}'

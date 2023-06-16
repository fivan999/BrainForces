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

    is_private = django.db.models.BooleanField(
        default=False,
        verbose_name='приватная',
        help_text='Приватная организация или нет',
    )

    is_active = django.db.models.BooleanField(
        default=False,
        verbose_name='активная',
        help_text='активная организация или нет',
    )

    class Meta:
        verbose_name = 'организация'
        verbose_name_plural = 'организации'

    def __str__(self) -> str:
        """строковое представление"""
        return self.name[:20]

    def get_absolute_url(self) -> str:
        """путь к organization detail"""
        return django.urls.reverse_lazy(
            'organization:profile', kwargs={'pk': self.pk}
        )

    def description_to_string_for_elastic(self) -> str:
        """
        elastic не может проиндексировать RichTextUploadingField
        поэтому прописываем его сами
        """
        return self.description


class OrganizationToUser(django.db.models.Model):
    """связь организации с пользователем"""

    objects = organization.managers.OrganizationToUserManager()

    class UserRoles(django.db.models.IntegerChoices):
        """роли пользователя в органицазии"""

        INVITED = 0, 'Приглашен'
        PARTICIPANT = 1, 'Участник'
        ADMIN = 2, 'Админ'
        CREATOR = 3, 'Создатель'

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


class OrganizationPost(django.db.models.Model):
    """объявление организации"""

    objects = organization.managers.OrganizationPostManager()

    name = django.db.models.CharField(
        max_length=150,
        verbose_name='название',
        help_text='Название объявления',
    )

    text = ckeditor_uploader.fields.RichTextUploadingField(
        verbose_name='текст', help_text='Текст поста'
    )

    is_private = django.db.models.BooleanField(
        default=False,
        verbose_name='приватный',
        help_text='Приватный пост или нет',
    )

    posted_by = django.db.models.ForeignKey(
        Organization,
        verbose_name='организация',
        help_text='Организация, написавшая пост',
        on_delete=django.db.models.CASCADE,
        related_name='posts',
    )

    class Meta:
        verbose_name = 'пост'
        verbose_name_plural = 'посты'

    def __str__(self) -> str:
        """строковое представление"""
        return self.name[:20]

    def text_to_string_for_elastic(self) -> str:
        """
        elastic не может проиндексировать RichTextField,
        поэтому прописываем его сами
        """
        return self.text


class CommentToOrganizationPost(django.db.models.Model):
    """моедль комментария к посту"""

    text = django.db.models.TextField(
        verbose_name='текст', help_text='Текст комментария'
    )

    user = django.db.models.ForeignKey(
        users.models.User,
        verbose_name='пользователь',
        help_text='Пользователь, котрый оставил комментарий',
        on_delete=django.db.models.CASCADE,
        related_name='comments',
    )

    post = django.db.models.ForeignKey(
        OrganizationPost,
        verbose_name='пост',
        help_text='Пост, к которому оставлен комментарий',
        on_delete=django.db.models.CASCADE,
        related_name='comments',
    )

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'комментарии'

    def __str__(self) -> str:
        """строковое представление"""
        return f'Комментарий {self.pk}'


class OrganizationPostLike(django.db.models.Model):
    """модель лайка на пост"""

    user = django.db.models.ForeignKey(
        to=users.models.User,
        verbose_name='пользователь',
        help_text='пользователь, поставивший лайк',
        on_delete=django.db.models.CASCADE,
        related_name='likes',
    )

    post = django.db.models.ForeignKey(
        to=OrganizationPost,
        verbose_name='пост',
        help_text='пост, под который поставлен лайк',
        on_delete=django.db.models.CASCADE,
        related_name='likes',
    )

    class Meta:
        verbose_name = 'лайк к посту'
        verbose_name_plural = 'лайки к постам'
        unique_together = ('post', 'user')

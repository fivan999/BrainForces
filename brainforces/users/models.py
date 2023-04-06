import transliterate

import django.contrib.auth.models
import django.db.models
import django.urls
from django.utils.translation import gettext_lazy as _

import core.models
import users.managers


def generate_image_path(obj: django.db.models.Model, filename: str) -> str:
    """генерируем файловый пусть к картинке"""
    filename = transliterate.translit(filename, 'ru', reversed=True)
    return f'users/{obj.user.pk}/{filename}'


class User(django.contrib.auth.models.AbstractUser):
    """кастомный пользователь"""

    objects = users.managers.UserManager()
    email = django.db.models.EmailField(
        _('email address'), blank=True, max_length=100, unique=True
    )
    login_attempts = django.db.models.IntegerField(
        default=0,
        verbose_name='неудачные попытки',
        help_text='Количество неудачных попыток входа в аккаунт',
    )

    class Meta(django.contrib.auth.models.AbstractUser.Meta):
        db_table = 'auth_user'
        swappable = 'AUTH_USER_MODEL'

    def get_absolute_url(self) -> str:
        """путь к user_detail"""
        return django.urls.reverse('users:user_detail', kwargs={'pk': self.pk})


class Profile(core.models.AbstractImageModel):
    """профиль пользователя"""

    user = django.db.models.OneToOneField(
        User,
        related_name='profile',
        verbose_name='Профиль',
        help_text='Профиль пользователя',
        on_delete=django.db.models.CASCADE,
        blank=True,
        null=True,
    )
    image = django.db.models.ImageField(
        blank=True,
        verbose_name='аватарка',
        help_text='Аватарка пользователя',
        upload_to=generate_image_path,
        null=True,
    )
    rating = django.db.models.PositiveIntegerField(
        verbose_name='рейтинг', help_text='Рейтинг пользователя', default=0
    )

    class Meta:
        verbose_name = 'профиль'
        verbose_name_plural = 'профили'

    def __str__(self) -> str:
        """строковое представление"""
        return f'Профиль пользователя {self.user.pk}'

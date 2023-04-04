import typing

import users.models

import django.contrib.auth.models
import django.core.exceptions
import django.db.models


class UserManager(django.contrib.auth.models.UserManager):
    """менеджер модели User"""

    def get_active_users(self) -> django.db.models.QuerySet:
        """возвращаем список активных пользователей"""
        return (
            self.get_queryset()
            .filter(is_active=True)
            .select_related('profile')
        )

    def get_only_useful_list_fields(self) -> django.db.models.QuerySet:
        """только нужные поля для одного пользователя"""
        return self.get_active_users().only(
            'username',
            'email',
            'profile__image',
            'first_name',
            'last_name',
            'profile__rating',
        )

    @classmethod
    def normalize_email(cls, email: str) -> str:
        """костомная нормализация email"""
        if not email:
            return ''
        username, domain = email.lower().strip().split('@')

        if '+' in username:
            username = username[: username.find('+')]

        if domain in ('ya.ru', 'yandex.ru'):
            username = username.replace('.', '-')
            domain = 'yandex.ru'
        elif domain == 'gmail.com':
            username = username.replace('.', '')

        return f'{username}@{domain}'

    def create_superuser(
        self, username: str, email: str, password: str, **extra_fields
    ) -> typing.Any:
        """переопределяем создание суперпользователя"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        email = self.normalize_email(email)
        if users.models.User.objects.filter(email=email).exists():
            raise django.core.exceptions.ValidationError(
                'Пользователь уже существует'
            )
        user = self.model(
            username=username,
            email=self.normalize_email(email),
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        users.models.Profile.objects.create(user=user)
        return user

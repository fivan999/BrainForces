import typing

import django.core.exceptions
import django.db.models
import django.forms

import users.models
import organization.models


class InviteToOrganizationForm(django.forms.Form):
    """форма приглашения нового пользователя"""

    username = django.forms.CharField(help_text='Имя или почта пользователя')

    def clean_username(self) -> typing.Union[str, None]:
        """валидируем пользователя"""
        username = self.cleaned_data['username']
        user = users.models.User.objects.filter(
            django.db.models.Q(username=username)
            | django.db.models.Q(email=username)
        ).first()
        if user is None:
            raise django.core.exceptions.ValidationError('Ошибка')
        self.cleaned_data['user_obj'] = user
        return username


class PostForm(django.forms.ModelForm):
    """форма создания поста организации"""

    class Meta:
        model = organization.models.OrganizationPost
        fields = ('name', 'text')

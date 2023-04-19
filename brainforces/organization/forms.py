import django.core.exceptions
import django.db.models
import django.forms

import organization.models
import users.models


class InviteToOrganizationForm(django.forms.Form):
    """форма приглашения нового пользователя"""

    username = django.forms.CharField(help_text='Имя или почта')

    def clean_username(self) -> str:
        """
        валидируем пользователя: имя или почта
        должны существовать
        """
        username = self.cleaned_data['username']
        user = users.models.User.objects.filter(
            django.db.models.Q(username=username)
            | django.db.models.Q(
                email=users.models.User.objects.normalize_email(username)
            )
        ).first()
        if user is None:
            raise django.core.exceptions.ValidationError('Ошибка')
        self.cleaned_data['user_obj'] = user
        return username


class PostForm(django.forms.ModelForm):
    """форма создания поста организации"""

    class Meta:
        model = organization.models.OrganizationPost
        fields = ('name', 'text', 'is_private')

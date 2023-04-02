import users.models

import django.contrib.auth.forms
import django.forms


class SignUpForm(django.contrib.auth.forms.UserCreationForm):
    """форма регистрации"""

    class Meta(django.contrib.auth.forms.UserCreationForm.Meta):
        fields = ('username', 'email', 'password1', 'password2')
        model = users.models.User

    def __init__(self, *args, **kwargs) -> None:
        """переопределяем поля"""
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Имя пользователя'
        self.fields['username'].help_text = 'Не более 150 символов. '
        'Только буквы, цифры и символы @/./+/-/_.'

        self.fields['email'].label = 'Почта'
        self.fields['email'].help_text = 'Введите адрес электронной почты'

        self.fields['password1'].label = 'Пароль'
        self.fields['password1'].help_text = 'Придумайте пароль'

        self.fields['password2'].label = 'Пароль еще раз'
        self.fields['password2'].help_text = 'Подтвердите пароль'


class CustomAuthenticationForm(django.contrib.auth.forms.AuthenticationForm):
    """форма авторизации"""

    def __init__(self, *args, **kwargs) -> None:
        """переопределяем поля"""
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Имя пользователя'
        self.fields['username'].help_text = 'Введите имя польвователя'

        self.fields['password'].label = 'Пароль'
        self.fields['password'].help_text = 'Введите пароль'


class CustomPasswordChangeForm(django.contrib.auth.forms.PasswordChangeForm):
    """форма смены пароля"""

    def __init__(self, *args, **kwargs) -> None:
        """переопределяем поля"""
        super().__init__(*args, **kwargs)
        self.fields['old_password'].label = 'Старый пароль'
        self.fields['old_password'].help_text = 'Введите старый пароль'

        self.fields['new_password1'].label = 'Новый пароль'
        self.fields['new_password1'].help_text = 'Придумайте пароль'

        self.fields['new_password2'].label = 'Пароль еще раз'
        self.fields['new_password2'].help_text = 'Подтвердите пароль'


class CustomPasswordResetForm(django.contrib.auth.forms.PasswordResetForm):
    """форма для отправки письма для восстановления пароля"""

    def __init__(self, *args, **kwargs) -> None:
        """переопределяем поля"""
        super().__init__(*args, **kwargs)
        self.fields['email'].label = 'Почта'
        self.fields[
            'email'
        ].help_text = 'Введите электронную почту, к которой привязан аккаунт'


class CustomSetPasswordForm(django.contrib.auth.forms.SetPasswordForm):
    """форма для нового пароля"""

    def __init__(self, *args, **kwargs) -> None:
        """переопределяем поля"""
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].label = 'Новый пароль'
        self.fields['new_password1'].help_text = 'Придумайте пароль'

        self.fields['new_password2'].label = 'Пароль еще раз'
        self.fields['new_password2'].help_text = 'Подтвердите пароль'


class CustomUserChangeForm(django.contrib.auth.forms.UserChangeForm):
    """форма изменения пользователя"""

    password = None

    class Meta:
        model = users.models.ShopUser
        fields = ('username', 'email', 'first_name', 'last_name')
        labels = {
            'username': 'Имя пользователя',
            'email': 'Почта',
            'first_name': 'Имя',
            'last_name': 'Фамилия',
        }
        help_texts = {
            'username': 'Введите имя пользователя',
            'email': 'Введите электронную почту',
            'first_name': 'Введите имя',
            'last_name': 'Введите фамилию',
        }


class ProfileChangeForm(django.forms.ModelForm):
    """форма изменения профиля"""

    class Meta:
        model = users.models.Profile
        fields = ('image',)
        labels = {'image': 'Аватарка'}
        help_texts = {'image': 'Загрузите аватарку'}

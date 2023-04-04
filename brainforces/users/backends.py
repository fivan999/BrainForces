import django.conf
import django.contrib
import django.contrib.auth.backends
import django.db.models

import users.models
import users.services


class EmailBackend(django.contrib.auth.backends.ModelBackend):
    """бекенд для аутентификации по почте"""

    def authenticate(
        self, request, username=None, password=None, **kwargs
    ) -> None:
        email = users.models.User.objects.normalize_email(username)
        try:
            user = users.models.User.objects.get(
                django.db.models.Q(email=email)
                | django.db.models.Q(username=username)
            )
        except users.models.User.DoesNotExist:
            return None
        if user.check_password(password):
            user.login_attempts = 0
            user.save()
            return user
        else:
            user.login_attempts += 1
            if user.login_attempts == django.conf.settings.LOGIN_ATTEMPTS:
                user.is_active = False
                django.contrib.messages.error(
                    request,
                    'Вы слишком много раз пытались '
                    'войти в аккаунт'
                    ', поэтому нам пришлось его деактивировать. '
                    'Ссылка для восстановления '
                    'отправлена на ваш email.',
                )
                users.services.activation_email(
                    request, 'users:reset_login_attempts', user
                )
            elif user.login_attempts > django.conf.settings.LOGIN_ATTEMPTS:
                django.contrib.messages.error(request, 'Проверьте свою почту')
            user.save()
        return None

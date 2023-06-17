import django.conf
import django.contrib
import django.contrib.auth.backends
import django.contrib.sites.shortcuts
import django.db.models
import django.http

import users.models
import users.tasks
import users.tokens


class EmailBackend(django.contrib.auth.backends.ModelBackend):
    """бекенд для аутентификации по почте"""

    def authenticate(
        self,
        request: django.http.HttpRequest,
        username: str = None,
        password: str = None,
        **kwargs
    ) -> None:
        """
        ищем пользователя с такой почтой,
        если пароль неправильный то количество неудачных
        попыток входа увеличивается
        отправляем письмо с реактивацией аккаунта если попыток много
        """
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
            user.backend = 'users.backends.EmailBackend'
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
                users.tasks.send_email_with_token.delay(
                    user_id=user.pk,
                    template_name='users/emails/activate_user.html',
                    subject='Активация аккаунта',
                    where_to='users:reset_login_attempts',
                    protocol='https' if request.is_secure() else 'http',
                    domain=django.contrib.sites.shortcuts.get_current_site(
                        request
                    ).domain,
                    token=users.tokens.token_7_days.make_token(user),
                )
            elif user.login_attempts > django.conf.settings.LOGIN_ATTEMPTS:
                django.contrib.messages.error(request, 'Проверьте свою почту')
            user.save()
        return None

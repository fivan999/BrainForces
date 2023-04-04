import users.tokens

import django.conf
import django.contrib.auth.models
import django.contrib.auth.tokens
import django.contrib.sites.shortcuts
import django.core.mail
import django.http
import django.template.loader
import django.utils.encoding
import django.utils.http


def activation_email(
    request: django.http.HttpRequest,
    where_to: str,
    user: django.contrib.auth.models.AbstractBaseUser,
) -> None:
    """создаем токен для активации аккаунта"""
    if where_to == 'users:reset_login_attempts':
        token = users.tokens.token_7_days.make_token(user)
    elif where_to == 'users:activate_user':
        token = django.contrib.auth.tokens.default_token_generator.make_token(
            user
        )
    message = django.template.loader.render_to_string(
        'users/activate_user.html',
        {
            'username': user.username,
            'domain': django.contrib.sites.shortcuts.get_current_site(
                request
            ).domain,
            'uid': django.utils.http.urlsafe_base64_encode(
                django.utils.encoding.force_bytes(user.pk)
            ),
            'token': token,
            'protocol': 'https' if request.is_secure() else 'http',
            'where_to': where_to,
        },
    )
    django.core.mail.send_mail(
        'Activate your account',
        message,
        django.conf.settings.EMAIL,
        [user.email],
        fail_silently=False,
    )

import celery

import django.core.mail
import django.template.loader
import django.utils.encoding
import django.utils.http

import users.models


@celery.shared_task
def send_email_with_token(
    user_id: int,
    template_name: str,
    subject: str,
    where_to: str,
    domain: str,
    protocol: str,
    token: str,
) -> None:
    """
    высылаем пользователю письмо с ссылкой
    для смены пароля или активации аккаунта
    token_generator - генератор токена для ссылки
    template_name - шаблон для генерации текста письма
    context - данные, которые могут быть высланы дополнительно
    например, при отправке почты из формы мы не имеем request,
    поэтому отдаем domain в context
    """
    user = users.models.User.objects.get(pk=user_id)
    message = django.template.loader.render_to_string(
        template_name,
        {
            'username': user.username,
            'domain': domain,
            'uid': django.utils.http.urlsafe_base64_encode(
                django.utils.encoding.force_bytes(user.pk)
            ),
            'token': token,
            'protocol': protocol,
            'where_to': where_to,
        },
    )
    django.core.mail.send_mail(
        subject=subject,
        message=message,
        from_email=None,
        recipient_list=[user.email],
        fail_silently=False,
    )

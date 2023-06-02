import http

import django.http
import django.shortcuts


def custom_404(
    request: django.http.HttpRequest, exception: Exception
) -> django.http.HttpResponse:
    """обработчки ошибки 404"""
    return django.shortcuts.render(
        request,
        template_name='errors/404.html',
        status=http.HTTPStatus.NOT_FOUND,
    )


def custom_500(request: django.http.HttpRequest) -> django.http.HttpResponse:
    """обработчик ошибки 404"""
    return django.shortcuts.render(
        request,
        template_name='errors/500.html',
        status=http.HTTPStatus.INTERNAL_SERVER_ERROR,
    )

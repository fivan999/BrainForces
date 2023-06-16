import http

import django_elasticsearch_dsl

import django.db.models
import django.http
import django.shortcuts
import django.views.generic

import core.elastic_services


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


class ElasticSearchListView(django.views.generic.ListView):
    """класс для поиска записей вместе с elasticsearch"""

    document_class: django_elasticsearch_dsl.Document  # документ для поиска
    search_fields: list  # список полей для поиска

    def get_default_queryset(self) -> django.db.models.QuerySet:
        """
        получаем кверисет, который
        нужно вызвать при отсутствии поискового запроса
        """
        ...

    def get_queryset(self) -> django.db.models.QuerySet:
        """получаем нужный queryset по поиску или без"""
        queryset = self.get_default_queryset()
        query = self.request.GET.get('query')
        if query:
            search_queryset = core.elastic_services.make_search_results(
                document_class=self.document_class,
                fields=['name', 'description'],
                query_text=query,
            ).distinct()
            queryset = queryset & search_queryset
        return queryset

import django_elasticsearch_dsl.search
import elasticsearch_dsl

import django.db.models


def make_search_results(
    document_class: django_elasticsearch_dsl.Document,
    fields: list,
    query_text: str,
) -> django.db.models.QuerySet:
    """
    результаты поиска elastic
    document_class - документ по которому производится поиск
    fields - поля, по которым искать
    query_text - сам запрос
    """
    query = elasticsearch_dsl.Q(
        'multi_match', query=query_text, fields=fields, fuzziness='auto'
    )
    results = document_class.search().query(query)
    return results.to_queryset()

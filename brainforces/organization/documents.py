import django_elasticsearch_dsl
import django_elasticsearch_dsl.registries

import organization.models


@django_elasticsearch_dsl.registries.registry.register_document
class OrganizationDocument(django_elasticsearch_dsl.Document):
    """документ elasticsearch для модели Organization"""

    description = django_elasticsearch_dsl.fields.TextField(
        attr='description_to_string_for_elastic'
    )

    class Index:
        name = 'организации'
        settings = {'number_of_shards': 1, 'number_of_replicas': 0}

    class Django:
        model = organization.models.Organization
        fields = ('name',)


@django_elasticsearch_dsl.registries.registry.register_document
class OrganizationPostDocument(django_elasticsearch_dsl.Document):
    """документ elasticsearch для модели OrganizationPost"""

    posted_by = django_elasticsearch_dsl.fields.ObjectField(
        properties={
            'id': django_elasticsearch_dsl.fields.IntegerField(),
            'name': django_elasticsearch_dsl.fields.TextField(),
        }
    )
    text = django_elasticsearch_dsl.fields.TextField(
        attr='text_to_string_for_elastic'
    )

    class Index:
        name = 'пост'
        settings = {'number_of_shards': 1, 'number_of_replicas': 0}

    class Django:
        model = organization.models.OrganizationPost
        fields = ('name',)

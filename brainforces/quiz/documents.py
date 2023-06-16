import django_elasticsearch_dsl
import django_elasticsearch_dsl.fields
import django_elasticsearch_dsl.registries

import quiz.models


@django_elasticsearch_dsl.registries.registry.register_document
class QuizDocument(django_elasticsearch_dsl.Document):
    """документ elasticsearch для модели Quiz"""

    description = django_elasticsearch_dsl.fields.TextField(
        attr='description_to_string_for_elastic'
    )
    organized_by = django_elasticsearch_dsl.fields.ObjectField(
        properties={
            'id': django_elasticsearch_dsl.fields.IntegerField(),
            'name': django_elasticsearch_dsl.fields.TextField(),
        }
    )

    class Index:
        name = 'викторины'
        settings = {'number_of_shards': 1, 'number_of_replicas': 0}

    class Django:
        model = quiz.models.Quiz
        fields = ('name',)

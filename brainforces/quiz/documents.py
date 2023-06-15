import quiz.models
import django_elasticsearch_dsl.fields
import django_elasticsearch_dsl
import django_elasticsearch_dsl.registries


@django_elasticsearch_dsl.registries.registry.register_document
class QuizDocument(django_elasticsearch_dsl.Document):
    """документ elasticsearch для модели Quiz"""

    description = django_elasticsearch_dsl.fields.TextField(
        attr='description_to_string_for_elastic'
    )
    organized_by = django_elasticsearch_dsl.fields.TextField(
        attr='organized_by_to_string_for_elastic'
    )

    class Index:
        name = 'викторины'
        settings = {'number_of_shards': 1, 'number_of_replicas': 0}

    class Django:
        model = quiz.models.Quiz
        fields = ('name',)

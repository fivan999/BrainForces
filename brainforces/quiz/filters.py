import django_filters

import quiz.models


class QuestionFilter(django_filters.FilterSet):
    """поиск по  вопросам"""

    class Meta:
        model = quiz.models.Question
        fields = {
            'name': ('search',),
            'text': ('search',),
            'difficulty': ('lte', 'gte'),
            'tags__name': ('icontains',),
        }

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        for field in self.form.fields.values():
            field.widget.attrs['class'] = 'form-control'

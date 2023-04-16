import django.forms

import quiz.models


class QuizQuestionsNumberForm(django.forms.Form):
    """форма выбора количества вопросов в викторине"""

    num_questions = django.forms.IntegerField(
        min_value=1, label='Количество вопросов',
        help_text='Введите количество вопросов в викторине'
    )


class QuizForm(django.forms.ModelForm):
    """форма создания викторины"""

    class Meta:
        model = quiz.models.Quiz
        fields = (
            'name',
            'description',
            'start_time',
            'duration',
            'is_rated',
            'is_private',
        )


class QuestionForm(django.forms.ModelForm):
    """форма создания вопроса"""

    variants = django.forms.CharField(
        label='Варианты ответа',
        help_text='Вводите варианты ответа каждый с новой строки'
                  ', у правильного на конце напишите right',
        widget=django.forms.widgets.Textarea(
            attrs={'rows': 5}
        )
    )

    class Meta:
        model = quiz.models.Question
        fields = ('name', 'text', 'difficulty')

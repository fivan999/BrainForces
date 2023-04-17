import django.core.exceptions
import django.forms

import quiz.models


class AnswerForm(django.forms.Form):
    answer = django.forms.ChoiceField(
        required=True,
        choices=[],
        widget=django.forms.RadioSelect(),
        label='Варианты ответа:',
    )


class QuizQuestionsNumberForm(django.forms.Form):
    """форма выбора количества вопросов в викторине"""

    num_questions = django.forms.IntegerField(
        min_value=1,
        label='Количество вопросов',
        help_text='Введите количество вопросов в викторине',
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
        widget=django.forms.widgets.Textarea(attrs={'rows': 5}),
    )

    class Meta:
        model = quiz.models.Question
        fields = ('name', 'text', 'difficulty')

    def clean_variants(self) -> list:
        """валидируем варианты ответа"""
        variants = list(
            map(lambda x: x.strip(), self.cleaned_data['variants'].split('\n'))
        )
        if len(variants) < 2:
            raise django.core.exceptions.ValidationError(
                'Слишком мало вариантов ответа'
            )
        if not any(map(lambda x: x.endswith('right'), variants)):
            raise django.core.exceptions.ValidationError(
                'Нет правильного варианта'
            )
        return variants

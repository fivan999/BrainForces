import django.contrib.admin.widgets
import django.core.exceptions
import django.forms
import django.utils.timezone

import quiz.models


class AnswerForm(django.forms.Form):
    """форма выбора варианта ответа"""

    answer = django.forms.ChoiceField(
        required=True,
        choices=[],
        widget=django.forms.RadioSelect(),
        label='Варианты ответа:',
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
        widgets = {
            'start_time': django.forms.DateTimeInput(
                attrs={
                    'class': 'form-control datetimepicker-input',
                    'data-target': '#datetimepicker1',
                }
            )
        }

    def clean_start_time(self):
        """
        валидируем время начала викторины
        она должна начинаться как минимум через 5 минут
        """
        start_time = self.cleaned_data['start_time']
        if (
            not start_time
            or not start_time - django.utils.timezone.now()
            >= django.utils.timezone.timedelta(minutes=5)
        ):
            raise django.core.exceptions.ValidationError(
                'Минимальное время начала - через 5 минут'
            )
        return start_time


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
        """
        валидируем варианты ответа
        их должно быть не меньше двух
        не менее одного правильного ответа
        """
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
        if any(map(lambda x: len(x) > 75, variants)):
            raise django.core.exceptions.ValidationError(
                'Слишком длинный вариант ответа'
            )
        return variants

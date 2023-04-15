import django.forms

import quiz.models


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

    class Meta:
        model = quiz.models.Question
        fields = ('name', 'text', 'difficulty')


class VariantForm(django.forms.ModelForm):
    """форма создания варианта ответа"""

    class Meta:
        model = quiz.models.Variant
        fields = ('text', 'is_correct')


QuestionFormSet = django.forms.inlineformset_factory(
    quiz.models.Quiz, quiz.models.Question, form=QuestionForm, extra=1
)

VariantFormSet = django.forms.inlineformset_factory(
    quiz.models.Question, quiz.models.Variant, form=VariantForm, extra=1
)

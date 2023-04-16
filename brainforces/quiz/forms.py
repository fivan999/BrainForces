import django.forms


class AnswerForm(django.forms.Form):
    CHOICES = []
    answers = django.forms.ChoiceField(
        required=True,
        choices=CHOICES,
        widget=django.forms.RadioSelect(),
        label='Ответы:',
    )

    def get_user_answer(self) -> int:
        answer = self.cleaned_data['answers']
        return answer[0]

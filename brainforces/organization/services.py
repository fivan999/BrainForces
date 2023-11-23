import typing

import django.contrib.messages
import django.http
import django.shortcuts

import organization.models
import quiz.forms


def get_post_by_user_organization_post_or_404(
    user_pk: int, org_pk: int, post_pk: int
) -> typing.Optional[organization.models.OrganizationPost]:
    """получаем объект поста по user_pk, org_pk и post_pk"""
    return (
        organization.models.OrganizationPost.objects.filter_user_access(
            user_pk=user_pk, org_pk=org_pk
        )
        .filter(pk=post_pk)
        .first()
    )


def process_quiz_creation_error(
    request: django.http.HttpRequest,
    question_formset: django.forms.BaseInlineFormSet,
    quiz_form: quiz.forms.QuizForm,
    context: dict,
) -> dict:
    django.contrib.messages.error(
        request,
        """
        Форма заполнена неверно.
        Если у вас было больше одного вопроса,
        нажимайте `Добавить вопрос`, чтобы увидеть всее ошибки
        """,
    )
    context['question_formset'] = question_formset
    context['form'] = quiz_form
    return context

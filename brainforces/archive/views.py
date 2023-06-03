import django.db.models
import django.shortcuts
import django.urls
import django.views.generic

import quiz.models


class ArchiveQuestionsView(django.views.generic.ListView):
    """список архивных вопросов"""

    template_name = 'archive/archive.html'
    context_object_name = 'questions'
    paginate_by = 70
    queryset = quiz.models.Question.objects.get_only_useful_list_fields()

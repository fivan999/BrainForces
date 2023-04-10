import django.db.models
import django.shortcuts
import django.urls
import django.views.generic

import quiz.models


class ArchiveView(django.views.generic.ListView):
    """список архивных вопросов"""

    template_name = 'archive/archive.html'
    context_object_name = 'questions'
    queryset = quiz.models.Question.objects.get_only_useful_list_fields()


class ArchiveSearchView(django.views.generic.ListView):
    """поиск архивных вопросов"""

    template_name = 'archive/search.html'
    context_object_name = 'questions'

    def get_queryset(self) -> django.db.models.QuerySet:
        queryset = quiz.models.Question.objects.get_only_useful_list_fields()
        searched = self.request.GET.get('searched', '')
        print(searched)
        if searched:
            queryset = (
                queryset.filter(
                    django.db.models.Q(name__iregex=searched)
                    | django.db.models.Q(text__iregex=searched)
                    | django.db.models.Q(tags__name__iregex=searched)
                )
            ).distinct()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['searched'] = self.request.GET.get('searched', '')
        return context


class ArchiveQuestionView(django.views.generic.DetailView):
    """архивный вопрос"""

    template_name = 'archive/question_detail.html'
    context_object_name = 'question'
    queryset = quiz.models.Question.objects.get_only_useful_list_fields()

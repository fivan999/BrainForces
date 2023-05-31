import django.db.models
import django.shortcuts
import django.urls
import django.views.generic

import core.forms
import quiz.models


class ArchiveQuestionsView(django.views.generic.ListView):
    """список архивных вопросов"""

    template_name = 'archive/archive.html'
    context_object_name = 'questions'
    paginate_by = 70

    def get_queryset(self) -> django.db.models.QuerySet:
        """
        обрабатываем поисковый запрос от пользователя:
        пользователь может искать по всем критериям,
        по имени вопроса, по тексту или названиям тегов
        """
        queryset = quiz.models.Question.objects.get_only_useful_list_fields()
        query = self.request.GET.get('query')
        search_by = int(self.request.GET.get('search_by', '1'))
        if query:
            if search_by == 1:
                queryset = (
                    queryset.filter(
                        django.db.models.Q(name__search=query)
                        | django.db.models.Q(text__search=query)
                        | django.db.models.Q(tags__name__icontains=query)
                    )
                ).distinct()
            elif search_by == 2:
                queryset = queryset.filter(name__search=query)
            elif search_by == 3:
                queryset = queryset.filter(text__search=query)
            else:
                queryset = queryset.filter(tags__name__search=query)
        return queryset

    def get_context_data(self, *args, **kwargs) -> dict:
        """дополняем контекст формой поиска"""
        context = super().get_context_data(*args, **kwargs)
        form = core.forms.SearchForm()
        form.fields['search_by'].choices = (
            (1, 'Все'),
            (2, 'Имя'),
            (3, 'Текст'),
            (4, 'Теги'),
        )
        context['form'] = form
        return context

import django.contrib.auth.mixins
import django.views.generic

import quiz.models


class HomeView(django.views.generic.ListView):
    """список викторин на главной странице"""

    template_name = 'homepage/homepage.html'
    context_object_name = 'quizes'
    queryset = quiz.models.Quiz.objects.get_only_useful_list_fields()

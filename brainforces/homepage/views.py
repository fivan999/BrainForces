import django.contrib.auth.mixins
import django.db.models
import django.views.generic

import quiz.models


class HomeView(django.views.generic.ListView):
    """список викторин на главной странице"""

    template_name = 'homepage/homepage.html'
    context_object_name = 'quizzes'
    paginate_by = 5
    queryset = list(
        quiz.models.Quiz.objects.get_only_useful_list_fields().filter(
            is_private=False
        )
    )

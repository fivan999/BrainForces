import django.contrib.auth.views
import django.urls

import quiz.views


app_name = 'quiz'

urlpatterns = [
    django.urls.path(
        '<int:quiz_id>/user_answers/',
        quiz.views.UserAnswersList.as_view(),
        name='user_answers_list',
    ),
    django.urls.path(
        '<int:pk>/',
        quiz.views.QuizDetailView.as_view(),
        name='quiz_detail',
    ),
    django.urls.path(
        'question/<int:quiz_id>/<int:question_number>/<int:pk>/',
        quiz.views.QuestionDetailView.as_view(),
        name='question_detail',
    ),
    django.urls.path(
        '<int:quiz_id>/standings/',
        quiz.views.StandingsList.as_view(),
        name='standings_list',
    ),
]

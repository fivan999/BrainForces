import django.urls

import quiz.views


app_name = 'quiz'

urlpatterns = [
    django.urls.path('', quiz.views.QuizListView.as_view(), name='list'),
    django.urls.path(
        '<int:pk>/',
        quiz.views.QuizDetailView.as_view(),
        name='quiz_detail',
    ),
    django.urls.path(
        '<int:pk>/user_answers/',
        quiz.views.UserAnswersList.as_view(),
        name='user_answers_list',
    ),
    django.urls.path(
        '<int:pk>/questions/<int:question_pk>/',
        quiz.views.QuestionDetailView.as_view(),
        name='question_detail',
    ),
    django.urls.path(
        '<int:pk>/standings/',
        quiz.views.StandingsList.as_view(),
        name='standings_list',
    ),
    django.urls.path(
        '<int:pk>/questions/',
        quiz.views.QuestionsView.as_view(),
        name='questions',
    ),
    django.urls.path(
        '<int:pk>/register/',
        quiz.views.QuizRegistrationView.as_view(),
        name='register',
    ),
    django.urls.path(
        '<int:pk>/make_results/',
        quiz.views.MakeQuizResultsView.as_view(),
        name='make_results',
    ),
]

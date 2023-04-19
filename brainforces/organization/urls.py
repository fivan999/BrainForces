import django.urls

import organization.views


app_name = 'organization'

urlpatterns = [
    django.urls.path(
        '<int:pk>/',
        organization.views.OrganizationMainView.as_view(),
        name='profile',
    ),
    django.urls.path(
        '<int:pk>/users/',
        organization.views.OrganizationUsersView.as_view(),
        name='users',
    ),
    django.urls.path(
        '<int:pk>/quizzes/',
        organization.views.OrganizationQuizzesView.as_view(),
        name='quizzes',
    ),
    django.urls.path(
        '<int:pk>/users/<int:user_pk>/delete/',
        organization.views.DeleteUserFromOrganizationView.as_view(),
        name='delete_user',
    ),
    django.urls.path(
        '<int:pk>/users/<int:user_pk>/update/<int:new_role>/',
        organization.views.UpdateUserOrganizationRoleView.as_view(),
        name='update_user_role',
    ),
    django.urls.path(
        '',
        organization.views.OrganizationListView.as_view(),
        name='list',
    ),
    django.urls.path(
        '<int:pk>/posts/',
        organization.views.OrganizationPostsView.as_view(),
        name='posts',
    ),
    django.urls.path(
        '<int:pk>/posts/<int:post_pk>/',
        organization.views.PostCommentsView.as_view(),
        name='post_detail',
    ),
    django.urls.path(
        '<int:pk>/create_quiz/',
        organization.views.ChooseQuizQuestionsNumber.as_view(),
        name='choose_questions_number',
    ),
    django.urls.path(
        '<int:pk>/create_quiz/<int:num_questions>/',
        organization.views.QuizCreateView.as_view(),
        name='create_quiz',
    ),
    django.urls.path(
        '<int:pk>/create_post/',
        organization.views.CreatePostView.as_view(),
        name='create_post',
    ),
]

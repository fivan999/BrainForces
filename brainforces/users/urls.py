import django.contrib.auth.views
import django.urls

import users.forms
import users.views


app_name = 'users'

urlpatterns = [
    django.urls.path(
        'login/',
        django.contrib.auth.views.LoginView.as_view(
            template_name='users/login.html',
            form_class=users.forms.CustomAuthenticationForm,
        ),
        name='login',
    ),
    django.urls.path(
        'logout/',
        django.contrib.auth.views.LogoutView.as_view(
            template_name='users/logout.html'
        ),
        name='logout',
    ),
    django.urls.path(
        'password_change/',
        django.contrib.auth.views.PasswordChangeView.as_view(
            template_name='users/password_change.html',
            form_class=users.forms.CustomPasswordChangeForm,
        ),
        name='password_change',
    ),
    django.urls.path(
        'password_change/done/',
        django.contrib.auth.views.PasswordChangeDoneView.as_view(
            template_name='users/password_change_done.html'
        ),
        name='password_change_done',
    ),
    django.urls.path(
        'password_reset/',
        django.contrib.auth.views.PasswordResetView.as_view(
            template_name='users/password_reset.html',
            form_class=users.forms.CustomPasswordResetForm,
        ),
        name='password_reset',
    ),
    django.urls.path(
        'password_reset/done/',
        django.contrib.auth.views.PasswordResetDoneView.as_view(
            template_name='users/password_reset_done.html'
        ),
        name='password_reset_done',
    ),
    django.urls.path(
        'reset/<uidb64>/<token>/',
        django.contrib.auth.views.PasswordResetConfirmView.as_view(
            template_name='users/password_reset_confirm.html',
            form_class=users.forms.CustomSetPasswordForm,
        ),
        name='password_reset_confirm',
    ),
    django.urls.path(
        'reset/done/',
        django.contrib.auth.views.PasswordResetCompleteView.as_view(
            template_name='users/password_reset_complete.html'
        ),
        name='password_reset_complete',
    ),
    django.urls.path(
        'signup/', users.views.SignupView.as_view(), name='signup'
    ),
    django.urls.path(
        'activate/<uidb64>/<token>/',
        users.views.ActivateUserView.as_view(),
        name='activate_user',
    ),
    django.urls.path(
        'profile/<int:pk>/',
        users.views.UserProfileView.as_view(),
        name='user_profile',
    ),
    django.urls.path(
        'profile/<int:pk>/change/',
        users.views.UserProfileChangeView.as_view(),
        name='user_profile_change',
    ),
    django.urls.path(
        'users/',
        users.views.UserListView.as_view(),
        name='user_list',
    ),
    django.urls.path(
        'reset_login_attempts/<uidb64>/<token>/',
        users.views.ResetLoginAttemptsView.as_view(),
        name='reset_login_attempts',
    ),
    django.urls.path(
        'profile/<int:pk>/answers/',
        users.views.UserAnswersView.as_view(),
        name='user_answers',
    ),
    django.urls.path(
        'profile/<int:pk>/quizzes/',
        users.views.UserQuizzesView.as_view(),
        name='user_quizzes',
    ),
]

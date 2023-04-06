import django.conf
import django.contrib
import django.contrib.auth
import django.contrib.auth.mixins
import django.contrib.auth.tokens
import django.db.models
import django.http
import django.shortcuts
import django.urls
import django.utils.encoding
import django.utils.http
import django.views
import django.views.generic
import django.views.generic.edit

import quiz.models
import users.forms
import users.models
import users.services
import users.tokens


class SignupView(django.views.generic.edit.FormView):
    """регистрация пользователя"""

    form_class = users.forms.SignUpForm
    template_name = 'users/signup.html'

    def get_success_url(self) -> str:
        """получаем адрес для редиректа в случае валидной формы"""
        return django.urls.reverse(
            'homepage:homepage',
        )

    def form_valid(
        self, form: users.forms.SignUpForm
    ) -> django.http.HttpResponsePermanentRedirect:
        """при валидной форме создается новый пользователь
        и активируется(сразу или письмо для активации приходит на почту)"""
        user = form.save(commit=False)
        user.is_active = django.conf.settings.USER_IS_ACTIVE
        user.save()
        profile = users.models.Profile(user=user)
        profile.save()
        if not django.conf.settings.USER_IS_ACTIVE:
            users.services.activation_email(
                self.request, 'users:activate_user', user
            )
            django.contrib.messages.success(
                self.request,
                f'На вашу почту {user.email} было '
                'отправлено письмо с активацией',
            )
        else:
            django.contrib.messages.success(
                self.request, 'Спасибо за регистрацию!'
            )
            django.contrib.auth.login(self.request, user)
        return super().form_valid(form)


class ActivateUserView(django.views.generic.View):
    """Активирует аккаунт пользователя"""

    def get(
        self, request: django.http.HttpRequest, uidb64: str, token: str
    ) -> django.http.HttpResponse:
        """активация аккаунта пользователя"""
        try:
            user = users.models.User.objects.get(
                pk=django.utils.encoding.force_str(
                    django.utils.http.urlsafe_base64_decode(uidb64)
                )
            )
        except Exception:
            user = None
        if (
            user
            and django.contrib.auth.tokens.default_token_generator.check_token(
                user, token
            )
        ):
            user.is_active = True
            user.save()
            django.contrib.auth.login(request, user)
            django.contrib.messages.success(
                request, 'Спасибо за активацию аккаунта'
            )
        else:
            django.contrib.messages.error(request, 'Ссылка активации неверна.')
        return django.shortcuts.redirect('homepage:homepage')


class ResetLoginAttemptsView(django.views.generic.View):
    def get(
        self, request: django.http.HttpRequest, uidb64: str, token: str
    ) -> django.http.HttpResponsePermanentRedirect:
        """активация аккаунта после превышения попыток"""
        try:
            user = users.models.User.objects.get(
                pk=django.utils.encoding.force_str(
                    django.utils.http.urlsafe_base64_decode(uidb64)
                )
            )
        except Exception:
            user = None
        if user and users.tokens.token_7_days.check_token(user, token):
            user.is_active = True
            django.contrib.messages.success(
                request,
                'Спасибо за активацию аккаунта,' 'теперь вы можете войти',
            )
            user.login_attempts = django.conf.settings.LOGIN_ATTEMPTS - 1
            user.save()
        else:
            django.contrib.messages.error(request, 'Ссылка активации неверна.')
        return django.shortcuts.redirect('homepage:homepage')


class UserProfileView(django.views.generic.DetailView):
    """информация о пользователе"""

    template_name = 'users/user_profile.html'
    queryset = users.models.User.objects.get_only_useful_detail_fields()


class UserProfileChangeView(
    django.contrib.auth.mixins.LoginRequiredMixin, django.views.generic.View
):
    """Профиль пользователя"""

    def get(
        self, request: django.http.HttpRequest, pk: int
    ) -> django.http.HttpResponse:
        if request.user.is_staff or request.user.id == pk:
            user_form = users.forms.CustomUserChangeForm(instance=request.user)
            profile_form = users.forms.ProfileChangeForm(
                instance=request.user.profile
            )
            context = {
                'forms': [user_form, profile_form],
            }
            return django.shortcuts.render(
                request, 'users/user_change.html', context=context
            )
        return django.http.Http404()

    def post(
        self, request: django.http.HttpRequest, pk: int
    ) -> django.http.HttpResponsePermanentRedirect:
        if request.user.is_staff or request.user.id == pk:
            user_form = users.forms.CustomUserChangeForm(
                request.POST, instance=request.user
            )
            profile_form = users.forms.ProfileChangeForm(
                request.POST, request.FILES, instance=request.user.profile
            )
            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                django.contrib.messages.success(
                    request, 'Профиль успешно изменен!'
                )
            return django.shortcuts.redirect('users:user_profile', pk=pk)
        return django.http.Http404()


class UserParticipatedQuizView(django.views.generic.ListView):
    """соревнования, в которых участвовал пользователь"""

    template_name = 'users/user_quizzes.html'
    context_object_name = 'quizzes'

    def get_queryset(self) -> django.db.models.QuerySet:
        return quiz.models.Quiz.objects.filter(users__id=self.kwargs['pk'])


class UserAnswersView(django.views.generic.ListView):
    """ответы пользователя на вопросы"""

    template_name = 'users/user_answers.html'
    context_object_name = 'answers'

    def get_queryset(self) -> django.db.models.QuerySet:
        return quiz.models.UserAnswer.objects.filter(
            user__pk=self.request.user.pk
        )

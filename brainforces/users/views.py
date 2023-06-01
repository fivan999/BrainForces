import django.conf
import django.contrib
import django.contrib.auth
import django.contrib.auth.forms
import django.contrib.auth.mixins
import django.contrib.auth.tokens
import django.contrib.auth.views
import django.contrib.messages
import django.db.models
import django.http
import django.shortcuts
import django.urls
import django.utils.encoding
import django.utils.http
import django.views
import django.views.generic
import django.views.generic.edit

import organization.models
import quiz.models
import users.backends
import users.forms
import users.mixins
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
        """
        при валидной форме создается новый пользователь
        и активируется(сразу или письмо для активации приходит на почту)
        """
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
            django.contrib.auth.login(
                self.request, user, backend='users.backends.EmailBackend'
            )
        return super().form_valid(form)


class ActivateUserView(django.views.generic.View):
    """Активирует аккаунт пользователя"""

    def get(
        self, request: django.http.HttpRequest, uidb64: str, token: str
    ) -> django.http.HttpResponse:
        """
        активация аккаунта пользователя
        если токен валидный
        """
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
            django.contrib.auth.login(
                request, user, backend='users.backends.EmailBackend'
            )
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
        """реактивация аккаунта после превышения попыток входа"""
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

    template_name = 'users/profile.html'
    queryset = users.models.User.objects.get_only_useful_detail_fields()


class UserListView(django.views.generic.ListView):
    """список пользователей по рейтингу"""

    template_name = 'users/list.html'
    context_object_name = 'users'
    queryset = (
        users.models.User.objects.get_only_useful_list_fields().order_by(
            '-profile__rating'
        )
    )
    paginate_by = 100


class UserProfileChangeView(
    users.mixins.UsernameMixinView,
    django.contrib.auth.mixins.LoginRequiredMixin,
    django.views.generic.View,
):
    """Профиль пользователя"""

    template_name = 'users/change.html'

    def get(
        self, request: django.http.HttpRequest, pk: int
    ) -> django.http.HttpResponse:
        """отдаем форму"""
        if request.user.id == pk:
            user_form = users.forms.CustomUserChangeForm(instance=request.user)
            profile_form = users.forms.ProfileChangeForm(
                instance=request.user.profile
            )
            context = {
                'forms': [user_form, profile_form],
            }
            return django.shortcuts.render(
                request, self.template_name, context=context
            )
        raise django.http.Http404()

    def post(
        self, request: django.http.HttpRequest, pk: int
    ) -> django.http.HttpResponsePermanentRedirect:
        """обрабатываем пост запрос"""
        if request.user.id == pk:
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
                return django.shortcuts.redirect('users:profile', pk=pk)
            else:
                return django.shortcuts.render(
                    request,
                    self.template_name,
                    {'forms': [user_form, profile_form]},
                )
        raise django.http.Http404()


class UserAnswersView(
    users.mixins.UsernameMixinView, django.views.generic.ListView
):
    """ответы пользователя на вопросы"""

    template_name = 'users/question_answers.html'
    context_object_name = 'answers'
    paginate_by = 40

    def get_queryset(self) -> django.db.models.QuerySet:
        """
        викторины, к которым относятся ответы на вопрос,
        могут быть приватными
        поэтому ответы должны быть либо если она не приватная,
        либо пользователь - участник организации,
        которая организовала викторину
        """
        user_pk = self.request.user.pk
        return (
            quiz.models.UserAnswer.objects.get_only_useful_list_fields()
            .filter(
                django.db.models.Q(
                    question__quiz__is_private=False,
                    question__quiz__organized_by__users__pk=user_pk,
                )
                | django.db.models.Q(question__quiz__is_private=False),
                user__pk=self.kwargs['pk'],
            )
            .distinct()
            .order_by('-time_answered')
        )


class UserQuizzesView(
    users.mixins.UsernameMixinView, django.views.generic.ListView
):
    """виторины, в которых участвовал пользователь"""

    template_name = 'users/quiz_results.html'
    context_object_name = 'results'
    paginate_by = 15

    def get_queryset(self) -> django.db.models.QuerySet:
        """
        викторины могут быть приватные,
        поэтому результаты должны быть либо если она не приватная,
        либо пользователь - участник организации,
        которая организовала викторину
        """
        return (
            quiz.models.QuizResults.objects.get_only_useful_list_fields()
            .filter(
                django.db.models.Q(
                    quiz__is_private=True,
                    quiz__organized_by__users__pk=self.request.user.pk,
                )
                | django.db.models.Q(quiz__is_private=False),
                user__pk=self.kwargs['pk'],
            )
            .distinct()
            .order_by('-quiz__start_time')
        )


class UserOrganizationsView(
    users.mixins.UsernameMixinView, django.views.generic.ListView
):
    """список организаций пользователя"""

    template_name = 'users/organizations.html'
    context_object_name = 'organizations'
    paginate_by = 15

    def get_queryset(self) -> django.db.models.QuerySet:
        """
        пользователь может смотреть как свои организации,
        так и чужие
        поэтому делаем проверку на приватность организации
        или принадлежность юзера к ней
        """
        org_to_user_manager = organization.models.OrganizationToUser.objects
        return (
            org_to_user_manager.get_active_organization_to_user()
            .filter(
                django.db.models.Q(organization__is_private=False)
                | django.db.models.Q(
                    organization__is_private=True,
                    organization__users__pk=self.request.user.pk,
                ),
                user__pk=self.kwargs['pk'],
            )
            .select_related('organization')
            .only('organization__name', 'role')
            .distinct()
        )


class CreateOrganizationView(
    users.mixins.UsernameMixinView, django.views.generic.edit.FormView
):
    """создание организации"""

    template_name = 'users/create_organization.html'
    form_class = users.forms.CreateOrganizationForm

    def get_context_data(self, *args, **kwargs) -> dict:
        """проверка на доступ"""
        context = super().get_context_data(*args, **kwargs)
        if self.request.user.pk != self.kwargs['pk']:
            raise django.http.Http404()
        return context

    def form_valid(
        self, form: users.forms.CreateOrganizationForm
    ) -> django.http.HttpResponse:
        """создаем объект организации"""
        org_obj = form.save()
        organization.models.OrganizationToUser.objects.create(
            organization=org_obj, user=self.request.user, role=3
        )
        if org_obj.is_active:
            return django.shortcuts.redirect(
                django.urls.reverse_lazy(
                    'organization:profile', kwargs={'pk': org_obj.pk}
                )
            )
        else:
            django.contrib.messages.success(
                self.request,
                'Организация создана, дождитесь одобрения администрации',
            )
            return django.shortcuts.redirect(
                django.urls.reverse_lazy('homepage:homepage')
            )

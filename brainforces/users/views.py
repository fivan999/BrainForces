import django.conf
import django.contrib
import django.contrib.auth
import django.contrib.auth.mixins
import django.contrib.auth.tokens
import django.http
import django.shortcuts
import django.urls
import django.utils.encoding
import django.utils.http
import django.views
import django.views.generic
import django.views.generic.edit

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


class ResetLoginAttempts(django.views.generic.View):
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


class UserListView(
    django.contrib.auth.mixins.PermissionRequiredMixin,
    django.views.generic.ListView,
):
    """список пользователей"""

    permission_required = 'is_active'
    template_name = 'users/user_list.html'
    context_object_name = 'users'
    queryset = users.models.User.objects.get_only_useful_list_fields()


class UserDetailView(
    django.contrib.auth.mixins.PermissionRequiredMixin,
    django.views.generic.DetailView,
):
    """детальная информация о пользователе"""

    permission_required = 'is_staff'
    template_name = 'users/user_detail.html'
    context_object_name = 'user'
    queryset = users.models.User.objects.get_only_useful_detail_fields()


class UserProfileView(
    django.contrib.auth.mixins.LoginRequiredMixin, django.views.generic.View
):
    """Профиль пользоватея"""

    template_name = 'users/signup.html'

    def get(
        self, request: django.http.HttpRequest
    ) -> django.http.HttpResponse:
        user_form = users.forms.CustomUserChangeForm(instance=request.user)
        profile_form = users.forms.ProfileChangeForm(
            instance=request.user.profile
        )
        context = {
            'user': django.shortcuts.get_object_or_404(
                users.models.User.objects.get_only_useful_detail_fields(),
                pk=request.user.pk,
            ),
            'forms': [user_form, profile_form],
        }
        return django.shortcuts.render(
            request, 'users/profile.html', context=context
        )

    def post(
        self, request: django.http.HttpRequest
    ) -> django.http.HttpResponsePermanentRedirect:
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
        return django.shortcuts.redirect('users:user_profile')

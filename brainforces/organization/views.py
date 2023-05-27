import django.contrib.auth.mixins
import django.contrib.messages
import django.db.models
import django.forms
import django.http
import django.shortcuts
import django.urls
import django.views.generic

import core.forms
import organization.forms
import organization.mixins
import organization.models
import quiz.forms
import quiz.models


class OrganizationMainView(django.views.generic.DetailView):
    """главная страница организации"""

    template_name = 'organization/profile.html'
    context_object_name = 'organization'

    def get_queryset(self) -> django.db.models.QuerySet:
        """организация либо открытая, либо пользователь - участник"""
        return organization.models.Organization.objects.filter_user_access(
            user_pk=self.request.user.pk
        ).only('name', 'description')

    def get_context_data(self, *args, **kwargs) -> dict:
        """
        дополняем контекст переменными:
        является ли пользователь участником организации
        является ли он ее администратором
        """
        context = super().get_context_data(*args, **kwargs)
        org_user_manager = organization.models.OrganizationToUser.objects
        user = (
            org_user_manager.get_organization_member(
                org_pk=self.kwargs['pk'], user_pk=self.request.user.pk
            )
            .only('role')
            .first()
        )
        context['is_group_member'] = user is not None
        context['user_is_admin'] = context[
            'is_group_member'
        ] and user.role in (2, 3)
        return context


class OrganizationListView(django.views.generic.ListView):
    """список организаций"""

    template_name = 'organization/list.html'
    paginate_by = 5
    context_object_name = 'organizations'

    def get_queryset(self) -> django.db.models.QuerySet:
        """
        получение объектов и поиск
        поиск либо по всем критериям,
        либо по названию и описанию по отдельности
        """
        queryset = (
            organization.models.Organization.objects.filter_user_access(
                self.request.user.pk
            )
            .annotate(count_users=django.db.models.Count('users__id'))
            .order_by('-count_users')
        )
        query = self.request.GET.get('query')
        search_by = int(self.request.GET.get('search_by', '1'))
        if query:
            if search_by == 1:
                queryset = (
                    queryset.filter(
                        django.db.models.Q(name__search=query)
                        | django.db.models.Q(description__search=query)
                    )
                ).distinct()
            elif search_by == 2:
                queryset = queryset.filter(name__search=query)
            elif search_by == 3:
                queryset = queryset.filter(description__search=query)
        return queryset

    def get_context_data(self, *args, **kwargs) -> dict:
        """дополняем контекст формой поиска"""
        context = super().get_context_data(*args, **kwargs)
        form = core.forms.SearchForm()
        form.fields['search_by'].choices = (
            (1, 'Все'),
            (2, 'Имя'),
            (3, 'Описание'),
        )
        context['form'] = form
        return context


class OrganizationUsersView(
    organization.mixins.UserIsOrganizationMemberMixin,
    django.views.generic.ListView,
):
    """страница с пользователями организации"""

    template_name = 'organization/users.html'
    context_object_name = 'users'
    paginate_by = 50

    def get_queryset(self) -> django.db.models.QuerySet:
        return (
            organization.models.OrganizationToUser.objects.filter(
                organization__pk=self.kwargs['pk']
            )
            .select_related('user')
            .only('user__username', 'role')
        )

    def get_context_data(self, *args, **kwargs) -> dict:
        """
        дополняем контекст формой и информацией о том,
        является ли пользователь админом группы
        """
        context = super().get_context_data(*args, **kwargs)
        if context['user_is_admin']:
            context['form'] = organization.forms.InviteToOrganizationForm()
        return context

    def post(
        self, request: django.http.HttpRequest, pk: int
    ) -> django.http.HttpResponsePermanentRedirect:
        """
        приглашаем пользователя в организацию
        проверки: валидна ли форма,
        существует ли организация,
        является ли пользователь администратором группы
        (только админ может пригласить)
        """
        form = organization.forms.InviteToOrganizationForm(
            request.POST or None
        )
        if form.is_valid():
            org_user_manager = organization.models.OrganizationToUser.objects
            user_obj = (
                org_user_manager.get_organization_admin(
                    org_pk=pk, user_pk=request.user.pk
                )
                .select_related('organization')
                .only('id', 'organization__id')
                .first()
            )

            if user_obj:
                try:
                    organization.models.OrganizationToUser.objects.create(
                        user=form.cleaned_data['user_obj'],
                        role=0,
                        organization=user_obj.organization,
                    )
                    django.contrib.messages.success(
                        request, 'Приглашение отправлено'
                    )
                except django.db.utils.IntegrityError:
                    django.contrib.messages.error(request, 'Ошибка')
            else:
                raise django.http.Http404()
        else:
            django.contrib.messages.error(request, 'Ошибка')
        return django.shortcuts.redirect(
            django.urls.reverse('organization:users', kwargs={'pk': pk})
        )


class JoinOrganizationView(
    django.contrib.auth.mixins.LoginRequiredMixin,
    organization.mixins.UserIsOrganizationMemberMixin,
    django.views.generic.View,
):
    """юзер присоединяется к публичной орге"""

    def get(
        self, request: django.http.HttpRequest, pk: int
    ) -> django.http.HttpResponsePermanentRedirect:
        context = self.get_context_data()
        if (
            not context['organization'].is_private
            and not context['is_group_member']
        ):
            organization.models.OrganizationToUser.objects.create(
                user=request.user, organization=context['organization'], role=1
            )
            django.contrib.messages.success(
                request, 'Вы успешно присоединились к организации!'
            )
            return django.shortcuts.redirect(
                django.urls.reverse_lazy(
                    'organization:profile', kwargs={'pk': pk}
                ),
            )
        raise django.http.Http404()


class OrganizationQuizzesView(
    organization.mixins.UserIsOrganizationMemberMixin,
    django.views.generic.ListView,
):
    """список соревнований организации"""

    template_name = 'organization/quizzes.html'
    context_object_name = 'quizzes'
    paginate_by = 5

    def get_queryset(self) -> django.db.models.QuerySet:
        """
        соревнования организации
        они могут быть приватными, поэтому нужно фильтровать
        """
        return quiz.models.Quiz.objects.filter_user_access(
            user_pk=self.request.user.pk, org_pk=self.kwargs['pk']
        )


class ActionWithUserView(django.views.generic.View):
    """
    получаем модель organizationtouser
    того кто спрашивает
    и того о ком спрашивают
    """

    def get(
        self, request: django.http.HttpRequest, pk: int, user_pk: int
    ) -> None:
        self.self_user = (
            organization.models.OrganizationToUser.objects.filter(
                organization__pk=pk,
                organization__is_active=True,
                user__pk=request.user.pk,
            )
            .only('role')
            .first()
        )
        self.target_user = (
            organization.models.OrganizationToUser.objects.filter(
                user__pk=user_pk,
                organization__pk=pk,
                organization__is_active=True,
            )
            .only('role')
            .first()
        )


class DeleteUserFromOrganizationView(ActionWithUserView):
    """удаляем пользователя из организации"""

    def get(
        self, request: django.http.HttpRequest, pk: int, user_pk: int
    ) -> django.http.HttpResponsePermanentRedirect:
        """
        пользователи должны существовать
        удаляющий должен быть выше по роли
        обычный участник не может удалить приглашенного (с ролью = 0)
        либо пользователь выходит из организации сам
        """
        super().get(request, pk, user_pk)
        if (
            self.self_user
            and self.target_user
            and (
                self.self_user.role > self.target_user.role
                and self.self_user.role != 1
                or self.request.user.pk == user_pk
            )
        ):
            self.target_user.delete()
            django.contrib.messages.success(request, 'Успешно')
        else:
            django.contrib.messages.error(request, 'Ошибка')
        return django.shortcuts.redirect(
            django.urls.reverse('organization:profile', kwargs={'pk': pk})
        )


class UpdateUserOrganizationRoleView(ActionWithUserView):
    """изменение статуса пользователя"""

    def get(
        self,
        request: django.http.HttpRequest,
        pk: int,
        user_pk: int,
        new_role: int,
    ) -> django.http.HttpResponsePermanentRedirect:
        super().get(request, pk, user_pk)
        """
        пользователи должны существовать,
        обновляющий статус должен быть выше по роли
        или пользователь принимает приглашение (с 0 до 1)
        """
        if (
            new_role in (1, 2)
            and self.self_user
            and self.target_user
            and (
                self.self_user.role > self.target_user.role
                or self.request.user.pk == user_pk
                and new_role == 1
            )
        ):
            self.target_user.role = new_role
            self.target_user.save()
            django.contrib.messages.success(request, 'Успешно')
        else:
            django.contrib.messages.error(request, 'Ошибка')
        return django.shortcuts.redirect(
            django.urls.reverse('organization:users', kwargs={'pk': pk})
        )


class OrganizationPostsView(
    organization.mixins.UserIsOrganizationMemberMixin,
    django.views.generic.ListView,
):
    """объявления организации"""

    template_name = 'organization/posts.html'
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self) -> django.db.models.QuerySet:
        """объявления могут быть приватными, поэтому нужна проверка"""
        return organization.models.OrganizationPost.objects.filter_user_access(
            self.request.user.pk, org_pk=self.kwargs['pk']
        )


class PostCommentsView(
    organization.mixins.UserIsOrganizationMemberMixin,
    django.views.generic.ListView,
):
    """комментарии к посту"""

    template_name = 'organization/post_comments.html'
    paginate_by = 50
    context_object_name = 'comments'

    def get_context_data(self, *args, **kwargs) -> dict:
        """
        получаем нужный пост и проверяем
        доступ пользователя к нему
        """
        context = super().get_context_data(*args, **kwargs)
        context['post'] = django.shortcuts.get_object_or_404(
            organization.models.OrganizationPost.objects.filter_user_access(
                self.request.user.pk, org_pk=self.kwargs['pk']
            ),
            pk=self.kwargs['post_pk'],
        )
        return context

    def get_queryset(self) -> django.db.models.QuerySet:
        """
        комментарии пользователей к посту
        """
        return (
            organization.models.CommentToOrganizationPost.objects.filter(
                post__pk=self.kwargs['post_pk']
            )
            .select_related('user')
            .only('user__username', 'text')
            .order_by('id')
        )

    def post(
        self, request: django.http.HttpResponse, pk: int, post_pk: int
    ) -> django.http.HttpResponsePermanentRedirect:
        """
        обрабатываем добавление комментария
        проверки: существование поста
        доступ пользователя
        """
        if not request.user.is_authenticated:
            raise django.http.Http404()
        comment_text = request.POST.get('comment_text')
        post = django.shortcuts.get_object_or_404(
            organization.models.OrganizationPost.objects.filter_user_access(
                self.request.user.pk, org_pk=self.kwargs['pk']
            ),
            pk=self.kwargs['post_pk'],
        )
        if comment_text:
            organization.models.CommentToOrganizationPost.objects.create(
                user=request.user, text=comment_text, post=post
            )
        return django.shortcuts.redirect(
            django.urls.reverse(
                'organization:post_detail',
                kwargs={'pk': pk, 'post_pk': post_pk},
            )
        )


class QuizCreateView(
    organization.mixins.IsAdminMixin,
    django.views.generic.edit.FormView,
):
    """создание викторины"""

    template_name = 'organization/create_quiz.html'
    form_class = quiz.forms.QuizForm

    def get_context_data(self, *args, **kwargs) -> dict:
        """
        дополняем контекст формсетом из форм с добавлением вопроса
        """
        self.kwargs['pk'] = int(self.kwargs['pk'])
        context = super().get_context_data(*args, **kwargs)
        question_formset = django.forms.inlineformset_factory(
            quiz.models.Quiz,
            quiz.models.Question,
            form=quiz.forms.QuestionForm,
            extra=50,
            max_num=50,
        )
        context['question_formset'] = question_formset()
        return context

    def post(
        self, request: django.http.HttpRequest, pk: int
    ) -> django.http.HttpResponse:
        """
        обрабатываем создание викторины
        создаем формсет из нужного количества вопросов,
        валидируем его
        проверяем на существование организации
        и админа организации с данным pk
        проходимся по всем вопросам, проверяем валидность,
        создаем вопросы и варианты,
        сохраняем квиз, вопросы и варианты ответов
        """
        context = self.get_context_data()
        quiz_form = self.form_class(request.POST or None)
        question_formset = django.forms.inlineformset_factory(
            quiz.models.Quiz,
            quiz.models.Question,
            form=quiz.forms.QuestionForm,
            extra=50,
        )(self.request.POST or None)
        if quiz_form.is_valid() and question_formset.is_valid():
            quiz_obj = quiz_form.save(commit=False)
            quiz_obj.organized_by = context['organization']
            quiz_obj.creator = request.user

            question_objects = list()
            variants_objects = list()

            for question in question_formset:
                question_obj = question.save(commit=False)
                question_obj.quiz = quiz_obj
                question_objects.append(question_obj)
                variants = question.cleaned_data['variants']
                for variant in variants:
                    if variant.endswith('right'):
                        variant_obj = quiz.models.Variant(
                            text=variant[: variant.rfind('right')],
                            question=question_obj,
                            is_correct=True,
                        )
                    else:
                        variant_obj = quiz.models.Variant(
                            text=variant,
                            question=question_obj,
                            is_correct=False,
                        )
                    variants_objects.append(variant_obj)
            quiz_obj.save()
            for item in question_objects:
                item.save()
            quiz.models.Variant.objects.bulk_create(variants_objects)
            message_text = 'Викторина отправлена на модерацию'
            if quiz_obj.is_published:
                message_text = 'Викторина создана'
            django.contrib.messages.success(request, message_text)
            return django.shortcuts.redirect(
                django.urls.reverse('organization:quizzes', kwargs={'pk': pk})
            )
        django.contrib.messages.error(
            request,
            """
            Форма заполнена неверно.
            Если у вас было больше одного вопроса,
            нажимайте Добавить вопрос, чтобы увидеть всее ошибки
            """,
        )
        context['question_formset'] = question_formset
        context['form'] = quiz_form
        return django.shortcuts.render(request, self.template_name, context)


class CreatePostView(
    organization.mixins.IsAdminMixin, django.views.generic.FormView
):
    """создание публикации организации"""

    form_class = organization.forms.PostForm
    template_name = 'organization/create_post.html'

    def post(
        self, request: django.http.HttpRequest, pk: int
    ) -> django.http.HttpResponse:
        """
        обрабатываем форму
        проверки: пользователь - админ организации
        форма валидная
        """
        form = self.form_class(request.POST or None)
        if form.is_valid():
            org_user_manager = organization.models.OrganizationToUser.objects
            user_obj = django.shortcuts.get_object_or_404(
                org_user_manager.get_organization_admin(
                    org_pk=pk, user_pk=request.user.pk
                )
                .select_related('organization')
                .only('id', 'organization__id')
            )
            post_obj = form.save(commit=False)
            post_obj.posted_by = user_obj.organization
            post_obj.save()
            return django.shortcuts.redirect(self.get_success_url())
        return django.shortcuts.render(
            request, self.template_name, {'form': form}
        )

    def get_success_url(self) -> str:
        """редиректим при успешной отправке формы"""
        return django.urls.reverse_lazy(
            'organization:posts', kwargs={'pk': self.kwargs['pk']}
        )

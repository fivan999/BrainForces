import zoneinfo

import mock
import parameterized

import django.conf
import django.db
import django.test
import django.urls
import django.utils.timezone

import organization.models
import quiz.models
import users.models


class OrganizationTest(django.test.TransactionTestCase):
    """тестируем организации"""

    reset_sequences = True

    fixtures = ['fixtures/organization/test.json']
    QUIZ_RIGHT_DATA = {
        'name': 'name',
        'description': 'description',
        'start_time': django.utils.timezone.datetime(2023, 1, 1, 0, 11),
        'duration': 11,
        'is_private': False,
        'is_rated': False,
        'quiz_question-0-name': 'name',
        'quiz_question-0-text': 'text',
        'quiz_question-0-difficulty': 1,
        'quiz_question-0-variants': 'bebraright\r\nbebra',
        'quiz_question-TOTAL_FORMS': 1,
        'quiz_question-INITIAL_FORMS': 0,
        'quiz_question-MAX_NUM_FORMS': 1000,
    }
    NAME_ERROR = {'name': ''}
    DESCRIPTION_ERROR = {'description': ''}
    START_TIME_ERROR = {
        'start_time': django.utils.timezone.datetime(2023, 1, 1, 0, 4)
    }
    DURATION_ERROR = {'duration': 9}
    QUESTION_NAME_ERROR = {'quiz_question-0-name': ''}
    QUESTION_TEXT_ERROR = {'quiz_question-0-text': ''}
    QUESTION_DIFFICULTY_ERROR = {'quiz_question-0-difficulty': -1}
    QUESTION_VARIANTS_ERROR_1 = {'quiz_question-0-variants': 'bebra\nbebra'}
    QUESTION_VARIANTS_ERROR_2 = {'quiz_question-0-variants': 'bebraright'}

    def test_organizations_list_status_code(self) -> None:
        """тестируем статус код страницы с организациями"""
        response = django.test.Client().get(
            django.urls.reverse('organization:list')
        )
        self.assertEqual(response.status_code, 200)

    def test_organization_list_correct_context(self) -> None:
        """тестируем корректный контекст страницы с организациями"""
        response = django.test.Client().get(
            django.urls.reverse('organization:list')
        )
        self.assertIn('organizations', response.context)

    def test_organization_list_correct_model(self) -> None:
        response = django.test.Client().get(
            django.urls.reverse('organization:list')
        )
        return self.assertTrue(
            all(
                map(
                    lambda x: isinstance(x, organization.models.Organization),
                    response.context['organizations'],
                )
            )
        )

    @parameterized.parameterized.expand(
        [
            ['', 2, 404],
            ['', 1, 200],
            ['user1', 1, 200],
            ['user1', 2, 200],
            ['user2', 1, 200],
            ['user2', 2, 404],
            ['user1', 3, 404],
        ]
    )
    def test_organization_main_page_user_access(
        self, username: str, org_pk: int, expected: int
    ) -> None:
        """тестируем вход на страницу с описанием организации"""
        client = django.test.Client()
        client.post(
            django.urls.reverse('users:login'),
            data={'username': username, 'password': 'password'},
        )
        response = client.get(
            django.urls.reverse('organization:profile', kwargs={'pk': org_pk})
        )
        self.assertEqual(response.status_code, expected)

    def test_organization_main_page_context(self) -> None:
        """тестируем контекст главной страницы организации"""
        response = django.test.Client().get(
            django.urls.reverse('organization:profile', kwargs={'pk': 1})
        )
        self.assertIn('organization', response.context)

    def test_organization_main_page_models(self) -> None:
        """тестируем модель на главной странице организации"""
        response = django.test.Client().get(
            django.urls.reverse('organization:profile', kwargs={'pk': 1})
        )
        self.assertEqual(
            type(response.context['organization']),
            organization.models.Organization,
        )

    @parameterized.parameterized.expand(
        [
            ['', 2, 404],
            ['', 1, 200],
            ['user1', 1, 200],
            ['user1', 2, 200],
            ['user2', 1, 200],
            ['user2', 2, 404],
            ['user1', 3, 404],
        ]
    )
    def test_organization_participants_user_access(
        self, username: str, org_pk: int, expected: int
    ) -> None:
        """тестируем вход на страницу со списком пользователей"""
        client = django.test.Client()
        client.post(
            django.urls.reverse('users:login'),
            data={'username': username, 'password': 'password'},
        )
        response = client.get(
            django.urls.reverse('organization:users', kwargs={'pk': org_pk})
        )
        self.assertEqual(response.status_code, expected)

    def test_organization_participants_context(self) -> None:
        """тестируем контекст страницы с участниками организации"""
        response = django.test.Client().get(
            django.urls.reverse('organization:users', kwargs={'pk': 1})
        )
        self.assertIn('users', response.context)

    def test_organization_participants_model(self) -> None:
        """тестируем модель на странице с пользователями"""
        response = django.test.Client().get(
            django.urls.reverse('organization:users', kwargs={'pk': 1})
        )
        self.assertTrue(
            all(
                map(
                    lambda x: isinstance(
                        x, organization.models.OrganizationToUser
                    ),
                    response.context['users'],
                )
            )
        )

    @parameterized.parameterized.expand(
        [
            # пользователь вступает в публичную оргу
            ['user1', 1, True],
            ['user3', 1, True],
            # орга неактивна
            ['user4', 4, False],
            ['user1', 4, False],
            # орга приватная
            ['user6', 2, False],
            ['user2', 2, False],
            # пользователь уже в орге
            ['user6', 1, False],
            ['user2', 1, False],
        ]
    )
    def test_organization_join(
        self, username: str, org_pk: int, expected: bool
    ) -> None:
        """тестируем возможность увступить в организацию"""
        client = django.test.Client()
        client.post(
            django.urls.reverse_lazy('users:login'),
            data={'username': username, 'password': 'password'},
        )
        members_before = organization.models.OrganizationToUser.objects.count()
        client.get(
            django.urls.reverse_lazy(
                'organization:join', kwargs={'pk': org_pk}
            )
        )
        members_after = organization.models.OrganizationToUser.objects.count()
        self.assertEqual(members_before + 1 == members_after, expected)

    @parameterized.parameterized.expand(
        [
            # админ добавляет пользователя
            ['user1', 2, 'user2', True],
            # админ добавляет пользователя в неактивную оргу
            ['user1', 3, 'user3', False],
            # не админ добавляет пользователя
            ['user2', 1, 'user1', False],
            # админ добавляет несуществующего пользователя
            ['user1', 2, 'bebrauser', False],
            # админ добавляет уже существующего пользователя
            ['user1', 2, 'user1', False],
        ]
    )
    def test_organization_participants_add_participant(
        self, username: str, org_pk: int, new_user: str, expected: bool
    ) -> None:
        """тестируем добавление пользователя в организацию"""
        client = django.test.Client()
        client.post(
            django.urls.reverse('users:login'),
            data={'username': username, 'password': 'password'},
        )
        count_before = organization.models.OrganizationToUser.objects.filter(
            organization__pk=org_pk
        ).count()
        with django.db.transaction.atomic():
            client.post(
                django.urls.reverse(
                    'organization:users', kwargs={'pk': org_pk}
                ),
                {'username': new_user},
            )
        count_after = organization.models.OrganizationToUser.objects.filter(
            organization__pk=org_pk
        ).count()
        self.assertEqual(count_after == count_before + 1, expected)

    @parameterized.parameterized.expand(
        [
            # админ удаляет участника
            ['user1', 2, 3, True],
            # админ удаляет участника из неактивной орги
            ['user1', 3, 2, False],
            # выход из группы
            ['user1', 2, 1, True],
            ['user3', 2, 3, True],
            # выход из неактивной группы
            ['user2', 3, 2, False],
            # пользователь из другой организации удаляет пользователя
            ['user3', 1, 2, False],
            # пользователь из другой организации удаляет пользователя
            ['user1', 1, 2, False],
            # участник удаляет админа
            ['user3', 2, 1, False],
        ]
    )
    def test_organization_participants_delete_participant(
        self, username: str, org_pk: int, user_pk: int, expected: bool
    ) -> None:
        """тестируем удаление пользователя из организации"""
        client = django.test.Client()
        client.post(
            django.urls.reverse('users:login'),
            data={'username': username, 'password': 'password'},
        )
        count_before = organization.models.OrganizationToUser.objects.filter(
            organization__pk=org_pk
        ).count()
        client.get(
            django.urls.reverse(
                'organization:delete_user',
                kwargs={'pk': org_pk, 'user_pk': user_pk},
            )
        )
        count_after = organization.models.OrganizationToUser.objects.filter(
            organization__pk=org_pk
        ).count()
        self.assertEqual(count_after == count_before - 1, expected)

    @parameterized.parameterized.expand(
        [
            # админ понижает другого админа
            ['user1', 2, 4, 1, True],
            # не админ понижает админа
            ['user3', 2, 1, 1, False],
            # админ повышает пользователя
            ['user4', 2, 3, 2, True],
            # админ повышает пользователя в неактивной орге
            ['user1', 3, 2, 2, False],
            # пользователь повышает сам себя
            ['user3', 2, 3, 2, False],
            # пользователь принимает приглашение в оргу (с 0 до 1)
            ['user5', 2, 5, 1, True],
            # пользователь из другой орги пытается
            # повысить пользователя
            ['user2', 2, 3, 2, False],
        ]
    )
    def test_organization_participants_change_role(
        self,
        username: str,
        org_pk: int,
        user_pk: int,
        new_role: int,
        expected: bool,
    ) -> None:
        """тестируем удаление пользователя из организации"""
        client = django.test.Client()
        client.post(
            django.urls.reverse('users:login'),
            data={'username': username, 'password': 'password'},
        )
        client.get(
            django.urls.reverse(
                'organization:update_user_role',
                kwargs={
                    'pk': org_pk,
                    'user_pk': user_pk,
                    'new_role': new_role,
                },
            )
        )
        user_after = organization.models.OrganizationToUser.objects.get(
            organization__pk=org_pk, user__pk=user_pk
        )
        self.assertEqual(user_after.role == new_role, expected)

    @parameterized.parameterized.expand(
        [
            ['', 2, 404],
            ['', 1, 200],
            ['user1', 1, 200],
            ['user1', 2, 200],
            ['user2', 1, 200],
            ['user2', 2, 404],
            ['user2', 3, 404],
        ]
    )
    def test_organization_quizzes_user_access(
        self, username: str, org_pk: int, expected: int
    ) -> None:
        """тестируем вход на страницу с викторинами организации"""
        client = django.test.Client()
        client.post(
            django.urls.reverse('users:login'),
            data={'username': username, 'password': 'password'},
        )
        response = client.get(
            django.urls.reverse('organization:quizzes', kwargs={'pk': org_pk})
        )
        self.assertEqual(response.status_code, expected)

    def test_organization_quizzes_context(self) -> None:
        """тестируем контекст страницы с викторинами организации"""
        response = django.test.Client().get(
            django.urls.reverse('organization:quizzes', kwargs={'pk': 1})
        )
        self.assertIn('quizzes', response.context)

    def test_organization_quizzes_model(self) -> None:
        """тестируем модель на странице с викторинами организации"""
        response = django.test.Client().get(
            django.urls.reverse('organization:quizzes', kwargs={'pk': 1})
        )
        self.assertTrue(
            all(
                map(
                    lambda x: isinstance(x, quiz.models.Quiz),
                    response.context['quizzes'],
                )
            )
        )

    @parameterized.parameterized.expand(
        [
            ['', 2, 404],
            ['', 1, 200],
            ['user1', 1, 200],
            ['user1', 2, 200],
            ['user2', 1, 200],
            ['user2', 2, 404],
            ['user1', 3, 404],
        ]
    )
    def test_organization_posts_user_access(
        self, username: str, org_pk: int, expected: int
    ) -> None:
        """тестируем вход на страницу с постами организации"""
        client = django.test.Client()
        client.post(
            django.urls.reverse('users:login'),
            data={'username': username, 'password': 'password'},
        )
        response = client.get(
            django.urls.reverse('organization:posts', kwargs={'pk': org_pk})
        )
        self.assertEqual(response.status_code, expected)

    def test_organization_posts_context(self) -> None:
        """тестируем контекст страницы с постами"""
        response = django.test.Client().get(
            django.urls.reverse('organization:posts', kwargs={'pk': 1})
        )
        self.assertIn('posts', response.context)

    def test_organization_posts_model(self) -> None:
        """тестируем модель на странице с постами организации"""
        response = django.test.Client().get(
            django.urls.reverse('organization:posts', kwargs={'pk': 1})
        )
        self.assertTrue(
            all(
                map(
                    lambda x: isinstance(
                        x, organization.models.OrganizationPost
                    ),
                    response.context['posts'],
                )
            )
        )

    @parameterized.parameterized.expand(
        [
            # организация и пост открытые
            ['user1', 1, 1, 200],
            # организация открыта, пост закрыт
            ['user1', 1, 3, 404],
            ['user2', 1, 1, 200],
            # организация закрыта, пост открыт
            ['user2', 2, 2, 404],
            # организация и пост закрыт
            ['user1', 2, 4, 200],
            ['user2', 2, 4, 404],
            # и то и то открыто, орга неактивная
            ['user1', 3, 5, 404],
        ]
    )
    def test_organization_post_user_access(
        self, username: str, org_pk: int, post_pk: int, expected: int
    ) -> None:
        """тестируем статус код страницы с детальным описанием поста"""
        client = django.test.Client()
        client.post(
            django.urls.reverse('users:login'),
            data={'username': username, 'password': 'password'},
        )
        response = client.get(
            django.urls.reverse(
                'organization:post_detail',
                kwargs={'pk': org_pk, 'post_pk': post_pk},
            )
        )
        self.assertEqual(response.status_code, expected)

    def test_organization_post_detail_context(self) -> None:
        """тестируем контекст страницы с детальным описанием поста"""
        client = django.test.Client()
        client.post(
            django.urls.reverse('users:login'),
            data={'username': 'user1', 'password': 'password'},
        )
        response = client.get(
            django.urls.reverse(
                'organization:post_detail', kwargs={'pk': 1, 'post_pk': 1}
            )
        )
        self.assertIn('post', response.context)
        self.assertIn('comments', response.context)

    @parameterized.parameterized.expand(
        [
            # редирект анонимусов на авторизацию
            ['', 1, 1, False],
            # организация и пост открытые
            ['user1', 1, 1, True],
            # организация открыта, пост закрыт
            ['user1', 1, 3, False],
            ['user2', 1, 1, True],
            # организация закрыта, пост открыт
            ['user2', 2, 2, False],
            # организация и пост закрыт
            ['user1', 2, 4, True],
            ['user2', 2, 4, False],
            # и то и то открыто, орга неактивная
            ['user2', 3, 5, False],
        ]
    )
    def test_create_comment_to_post(
        self, username: str, org_pk: int, post_pk: int, expected: bool
    ) -> None:
        """тестируем создание комментария к посту"""
        client = django.test.Client()
        client.post(
            django.urls.reverse('users:login'),
            data={'username': username, 'password': 'password'},
        )
        comments_before = (
            organization.models.CommentToOrganizationPost.objects.count()
        )
        client.post(
            django.urls.reverse(
                'organization:post_detail',
                kwargs={'pk': org_pk, 'post_pk': post_pk},
            ),
            data={'comment_text': 'test text'},
        )
        comments_after = (
            organization.models.CommentToOrganizationPost.objects.count()
        )
        self.assertEqual(comments_before + 1 == comments_after, expected)

    @parameterized.parameterized.expand(
        [
            # админы создают пост
            # орга активная
            ['user1', 2, True],
            ['user4', 2, True],
            ['user6', 1, True],
            # орга неактивная
            ['user1', 3, False],
            # не админы создают пост
            ['', 2, False],
            ['', 1, False],
            ['user3', 1, False],
            ['user3', 2, False],
        ]
    )
    def test_create_organization_post(
        self, username: str, org_pk: int, expected: bool
    ) -> None:
        """тестируем создание поста в организации"""
        client = django.test.Client()
        client.post(
            django.urls.reverse('users:login'),
            data={'username': username, 'password': 'password'},
        )
        posts_before = organization.models.OrganizationPost.objects.count()
        client.post(
            django.urls.reverse(
                'organization:create_post', kwargs={'pk': org_pk}
            ),
            data={'name': 'test', 'text': 'test'},
        )
        posts_after = organization.models.OrganizationPost.objects.count()
        self.assertEqual(posts_before + 1 == posts_after, expected)

    @parameterized.parameterized.expand(
        [
            # админы
            # орга активная
            ['user1', 2, 200],
            ['user4', 2, 200],
            ['user6', 1, 200],
            ['user6', 1, 200],
            # орга неактивная
            ['user1', 3, 404],
            # не админы
            ['', 2, 404],
            ['', 1, 404],
            ['user3', 1, 404],
            ['user3', 2, 404],
        ]
    )
    def test_organization_create_quiz_user_access(
        self, username: str, org_pk: int, expected: int
    ) -> None:
        """тестируем доступ к странице с созданием викторины"""
        client = django.test.Client()
        client.post(
            django.urls.reverse('users:login'),
            data={'username': username, 'password': 'password'},
        )
        response = client.get(
            django.urls.reverse(
                'organization:create_quiz',
                kwargs={'pk': org_pk},
            )
        )
        self.assertEqual(response.status_code, expected)

    @parameterized.parameterized.expand(
        [
            # ошибки формы
            ['user1', 2, NAME_ERROR, False],
            ['user1', 2, DESCRIPTION_ERROR, False],
            ['user1', 2, START_TIME_ERROR, False],
            ['user1', 2, DURATION_ERROR, False],
            ['user1', 2, QUESTION_NAME_ERROR, False],
            ['user1', 2, QUESTION_TEXT_ERROR, False],
            ['user1', 2, QUESTION_DIFFICULTY_ERROR, False],
            ['user1', 2, QUESTION_VARIANTS_ERROR_1, False],
            ['user1', 2, QUESTION_VARIANTS_ERROR_2, False],
            # все хорошо
            ['user1', 2, {}, True],
            # не админ
            ['user3', 2, {}, False],
            # орга неактивная
            ['user1', 3, {}, False],
        ]
    )
    @mock.patch(
        'django.utils.timezone.now',
        lambda: django.utils.timezone.datetime(
            2023,
            1,
            1,
            tzinfo=zoneinfo.ZoneInfo(django.conf.settings.TIME_ZONE),
        ),
    )
    def test_organization_create_quiz(
        self, username: str, org_pk: int, form_data: dict, expected: bool
    ) -> None:
        """тестируем создание квиза"""
        client = django.test.Client()
        client.post(
            django.urls.reverse('users:login'),
            data={'username': username, 'password': 'password'},
        )
        quizzes_before = quiz.models.Quiz.objects.count()
        questions_before = quiz.models.Question.objects.count()
        variants_before = quiz.models.Variant.objects.count()
        client.post(
            django.urls.reverse(
                'organization:create_quiz',
                kwargs={'pk': org_pk},
            ),
            data=self.QUIZ_RIGHT_DATA | form_data,
        )
        quizzes_after = quiz.models.Quiz.objects.count()
        questions_after = quiz.models.Question.objects.count()
        variants_after = quiz.models.Variant.objects.count()
        self.assertEqual(quizzes_before + 1 == quizzes_after, expected)
        self.assertEqual(questions_before + 1 == questions_after, expected)
        self.assertEqual(variants_before + 2 == variants_after, expected)

    @parameterized.parameterized.expand(
        [
            # не залогинился
            ['', 1, 1, 'like', False],
            # орга приватная, не участник
            ['user6', 2, 2, 'like', False],
            ['user6', 2, 2, 'unlike', False],
            # пост приватный, не участник
            ['user3', 1, 3, 'like', False],
            ['user3', 1, 3, 'unlike', False],
            # условия соблюдены
            ['user1', 1, 6, 'like', True],
            ['user1', 1, 1, 'unlike', True],
        ]
    )
    def test_user_can_like_or_unlike_post(
        self,
        username: str,
        org_pk: int,
        post_pk: int,
        action: str,
        expected: bool,
    ) -> None:
        """тестируем возможность пользователя лайкнуть и un лайкнуть пост"""
        client = django.test.Client()
        client.post(
            django.urls.reverse('users:login'),
            data={'username': username, 'password': 'password'},
        )
        delta = 1 if action == 'like' else -1
        likes_before = organization.models.OrganizationPostLike.objects.count()
        client.post(
            django.urls.reverse(
                'organization:like_post',
                kwargs={'pk': org_pk, 'post_pk': post_pk},
            ),
            data={'action': action},
        )
        likes_after = organization.models.OrganizationPostLike.objects.count()
        self.assertEqual(likes_before + delta == likes_after, expected)

    def tearDown(self) -> None:
        """удаление тестовых данных"""
        users.models.User.objects.all().delete()
        organization.models.Organization.objects.all().delete()
        super().tearDown()

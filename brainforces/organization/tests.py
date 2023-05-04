import parameterized

import django.db
import django.test
import django.urls

import organization.models
import quiz.models
import users.models


class OrganizationTest(django.test.TestCase):
    """тестируем организации"""

    fixtures = ['fixtures/organization/test.json']

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

    def test_organization_main_page_status_code(self) -> None:
        """тестируем статус код главной страницы организации"""
        response = django.test.Client().get(
            django.urls.reverse('organization:profile', kwargs={'pk': 1})
        )
        self.assertEqual(response.status_code, 200)

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
            ['user1', 1, True],
            ['user1', 2, True],
            ['user2', 1, True],
            ['user2', 2, False],
        ]
    )
    def test_organization_main_page_user_access(
        self, username: str, org_pk: int, expected: bool
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
        self.assertEqual(response.status_code == 200, expected)

    def test_organization_participants_status_code(self) -> None:
        """тестируем статус код страницы с участниками"""
        response = django.test.Client().get(
            django.urls.reverse('organization:users', kwargs={'pk': 1})
        )
        self.assertEqual(response.status_code, 200)

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
            ['user1', 1, True],
            ['user1', 2, True],
            ['user2', 1, True],
            ['user2', 2, False],
        ]
    )
    def test_organization_participants_user_access(
        self, username: str, org_pk: int, expected: bool
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
        self.assertEqual(response.status_code == 200, expected)

    @parameterized.parameterized.expand(
        [
            # админ добавляет пользователя
            ['user1', 2, 'user2', True],
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
            # выход из группы
            ['user1', 2, 1, True],
            # выход из группы
            ['user3', 2, 3, True],
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

    def test_organization_quizzes_status_code(self) -> None:
        """тестируем статус код страницы с викторинами организации"""
        response = django.test.Client().get(
            django.urls.reverse('organization:quizzes', kwargs={'pk': 1})
        )
        self.assertEqual(response.status_code, 200)

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
            ['user1', 1, True],
            ['user1', 2, True],
            ['user2', 1, True],
            ['user2', 2, False],
        ]
    )
    def test_organization_quizzes_user_access(
        self, username: str, org_pk: int, expected: bool
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
        self.assertEqual(response.status_code == 200, expected)

    def test_organization_posts_status_code(self) -> None:
        """тестируем статус код страницы с постами организации"""
        response = django.test.Client().get(
            django.urls.reverse('organization:posts', kwargs={'pk': 1})
        )
        self.assertEqual(response.status_code, 200)

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
            ['user1', 1, True],
            ['user1', 2, True],
            ['user2', 1, True],
            ['user2', 2, False],
        ]
    )
    def test_organization_posts_user_access(
        self, username: str, org_pk: int, expected: bool
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
        self.assertEqual(response.status_code == 200, expected)

    # @parameterized.parameterized.expand(
    #     [
    #         ['user1', 1, True],
    #         ['user1', 2, True],
    #         ['user2', 1, True],
    #         ['user2', 2, False],
    #     ]
    # )
    # def test_organization_post_detail_status_code(self) -> None:
    #     """тестируем статус код страницы с детальным описанием поста"""
    #     response = django.test.Client().get(
    #         django.urls.reverse(
    #             'organization:post_detail', kwargs={'pk': 1, 'post_pk': 1}
    #         )
    #     )
    #     self.assertEqual(response.status_code, 200)

    # def test_organization_post_detail_context(self) -> None:
    #     """тестируем контекст страницы с детальным описанием поста"""
    #     response = django.test.Client().get(
    #         django.urls.reverse(
    #             'organization:post_detail', kwargs={'pk': 1, 'post_pk': 1}
    #         )
    #     )
    #     self.assertIn('post', response.context)
    #     self.assertIn('comments', response.context)

    def tearDown(self) -> None:
        """удаление тестовых данных"""
        users.models.User.objects.all().delete()
        organization.models.Organization.objects.all().delete()
        super().tearDown()

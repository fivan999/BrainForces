import freezegun
import parameterized

import django.conf
import django.core
import django.test
import django.test.utils
import django.urls

import users.models


@django.test.utils.override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class UserTests(django.test.TransactionTestCase):
    """тестируем пользователя"""

    reset_sequences = True

    register_data = {
        'username': 'aboba',
        'email': 'aboba@yandex.ru',
        'password1': 'ajdfgbjuygfrb',
        'password2': 'ajdfgbjuygfrb',
    }

    def test_user_register_status_code(self) -> None:
        """тестируем статус код страницы регистрации"""
        response = django.test.Client().get(
            django.urls.reverse('users:signup')
        )
        self.assertEqual(response.status_code, 200)

    def test_user_register_context(self) -> None:
        """тестируем контекст страницы регистрации"""
        response = django.test.Client().get(
            django.urls.reverse('users:signup')
        )
        self.assertIn('form', response.context)

    def test_user_register_redirect(self) -> None:
        """тестируем редирект на главную страницу"""
        response = django.test.Client().post(
            django.urls.reverse('users:signup'),
            self.register_data,
            follow=True,
        )
        self.assertRedirects(
            response, django.urls.reverse('homepage:homepage')
        )

    def test_user_register_success(self) -> None:
        """тестируем появление записи в бд"""
        user_count = users.models.User.objects.count()
        django.test.Client().post(
            django.urls.reverse('users:signup'),
            self.register_data,
            follow=True,
        )
        self.assertEqual(users.models.User.objects.count(), user_count + 1)

    @django.test.override_settings(USER_IS_ACTIVE=False)
    def test_user_not_is_active(self) -> None:
        """тестируем неактивность пользователя"""
        django.test.Client().post(
            django.urls.reverse('users:signup'),
            self.register_data,
            follow=True,
        )
        self.assertFalse(users.models.User.objects.get(pk=1).is_active)

    @django.test.override_settings(USER_IS_ACTIVE=True)
    def test_user_is_active(self) -> None:
        """тестируем активность пользователя"""
        django.test.Client().post(
            django.urls.reverse('users:signup'),
            self.register_data,
            follow=True,
        )
        self.assertTrue(users.models.User.objects.get(pk=1).is_active)

    @django.test.override_settings(USER_IS_ACTIVE=False)
    def test_user_activation(self) -> None:
        """тестируем активацию пользователя"""
        client = django.test.Client()
        client.post(
            django.urls.reverse('users:signup'),
            self.register_data,
            follow=True,
        )
        text = django.core.mail.outbox[0].body
        text = text[text.find('http') : text.rfind('С уважением')].strip('\n')
        client.get(text)
        self.assertTrue(users.models.User.objects.get(pk=1).is_active)

    @django.test.override_settings(USER_IS_ACTIVE=False)
    def test_user_activation_error(self) -> None:
        """тестируем ошибку активации юзера"""
        client = django.test.Client()
        with freezegun.freeze_time('2023-01-01 00:00:00'):
            client.post(
                django.urls.reverse('users:signup'),
                self.register_data,
                follow=True,
            )
        with freezegun.freeze_time('2023-01-01 13:00:00'):
            text = django.core.mail.outbox[0].body
            text = text[text.find('http') : text.rfind('С уважением')].strip(
                '\n'
            )
            client.get(text)
            self.assertFalse(users.models.User.objects.get(pk=1).is_active)

    @parameterized.parameterized.expand(
        [
            [register_data['username'], register_data['password1'], True],
            [register_data['email'], register_data['password1'], True],
            [register_data['username'], 'awrgfkjuagvwf', False],
            ['qwertyuiop[]', register_data['password1'], False],
        ]
    )
    @django.test.override_settings(USER_IS_ACTIVE=True)
    def test_user_authenticate(
        self, username: str, password: str, expected: bool
    ) -> None:
        """проверяем возможность аутентификации"""
        client = django.test.Client()
        client.post(
            django.urls.reverse('users:signup'),
            self.register_data,
            follow=True,
        )
        client.get(django.urls.reverse('users:logout'), follow=True)
        response = client.post(
            django.urls.reverse('users:login'),
            {'username': username, 'password': password},
            follow=True,
        )
        self.assertEqual(response.context['user'].is_authenticated, expected)

    @parameterized.parameterized.expand(
        [
            ['aboba@ya.ru', 'aboba@yandex.ru'],
            ['ABOBA@yA.ru', 'aboba@yandex.ru'],
            ['abo.ba.+ger@gmail.com', 'aboba@gmail.com'],
            ['ABo.ba.+ger@gmail.com', 'aboba@gmail.com'],
        ]
    )
    def test_user_normalize_email(self, email: str, expected: str) -> None:
        """тестируем валидацию почты"""
        django.test.Client().post(
            django.urls.reverse('users:signup'),
            {
                'username': self.register_data['username'],
                'email': email,
                'password1': self.register_data['password1'],
                'password2': self.register_data['password2'],
            },
            follow=True,
        )
        self.assertEqual(users.models.User.objects.get(pk=1).email, expected)

    @django.test.override_settings(USER_IS_ACTIVE=True)
    def test_user_deactivation(self) -> None:
        """тестируем деактивацию профиля в авторизации"""
        client = django.test.Client()
        client.post(
            django.urls.reverse('users:signup'),
            self.register_data,
            follow=True,
        )
        for _ in range(django.conf.settings.LOGIN_ATTEMPTS):
            client.post(
                django.urls.reverse('users:login'),
                {
                    'username': self.register_data['username'],
                    'password': 'testbeb',
                },
                follow=True,
            )
        self.assertFalse(users.models.User.objects.get(pk=1).is_active)

    @django.test.override_settings(USER_IS_ACTIVE=True)
    def test_user_reactivation_success(self) -> None:
        """тестируем реактивацию профиля"""
        client = django.test.Client()
        client.post(
            django.urls.reverse('users:signup'),
            self.register_data,
            follow=True,
        )
        user = users.models.User.objects.get(pk=1)
        for _ in range(django.conf.settings.LOGIN_ATTEMPTS):
            client.post(
                django.urls.reverse('users:login'),
                {'username': user.username, 'password': 'testbeb'},
                follow=True,
            )
        text = django.core.mail.outbox[0].body
        text = text[text.find('http') : text.rfind('С уважением')].strip('\n')
        client.get(text)
        self.assertTrue(users.models.User.objects.get(pk=1).is_active)

    @django.test.override_settings(USER_IS_ACTIVE=True)
    def test_user_reactivation_error(self) -> None:
        """тестируем ошибку реактивации профиля"""
        with freezegun.freeze_time('2023-01-01'):
            client = django.test.Client()
            client.post(
                django.urls.reverse('users:signup'),
                self.register_data,
                follow=True,
            )
            user = users.models.User.objects.get(pk=1)
            for _ in range(django.conf.settings.LOGIN_ATTEMPTS):
                client.post(
                    django.urls.reverse('users:login'),
                    {'username': user.username, 'password': 'testbeb'},
                    follow=True,
                )
        with freezegun.freeze_time('2023-01-10'):
            text = django.core.mail.outbox[0].body
            text = text[text.find('http') : text.rfind('С уважением')].strip(
                '\n'
            )
            client.get(text)
            self.assertFalse(users.models.User.objects.get(pk=1).is_active)

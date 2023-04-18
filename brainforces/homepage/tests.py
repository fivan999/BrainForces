import django.test
import django.urls

import organization.models


class HomeTests(django.test.TestCase):
    """теста на приложение homepage"""

    def test_homepage_status_code(self) -> None:
        """тестируем статус код главной страницы"""
        response = django.test.Client().get(
            django.urls.reverse('homepage:homepage')
        )
        self.assertEqual(response.status_code, 200)

    def test_homepage_context(self) -> None:
        """тестируем контекст главной страницы"""
        response = django.test.Client().get(
            django.urls.reverse('homepage:homepage')
        )
        self.assertIn('posts', response.context)

    def test_homepage_model(self) -> None:
        """тестиуем правильную модель на странице"""
        response = django.test.Client().get(
            django.urls.reverse('homepage:homepage')
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

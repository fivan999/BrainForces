import django.test

import quiz.models


class ArchiveTests(django.test.TestCase):
    """тестируем архив"""

    fixtures = ['fixtures/archive/test.json']

    def test_archive_questions_status_code(self) -> None:
        """тестируем статус код главной страницы архива"""
        response = django.test.Client().get(
            django.urls.reverse('archive:archive')
        )
        self.assertEqual(response.status_code, 200)

    def test_archive_questions_context(self) -> None:
        """тестируем контекст главной страницы архива"""
        response = django.test.Client().get(
            django.urls.reverse('archive:archive')
        )
        self.assertIn('questions', response.context)

    def test_archive_questions_model(self) -> None:
        """тестируем правильную модель главной страницы архива"""
        response = django.test.Client().get(
            django.urls.reverse('archive:archive')
        )
        self.assertTrue(
            all(
                map(
                    lambda x: isinstance(x, quiz.models.Question),
                    response.context['questions'],
                )
            )
        )

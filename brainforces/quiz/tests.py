import django.test
import django.urls

import quiz.models


class QuizTests(django.test.TestCase):
    """тестируем функционал викторины"""

    fixtures = ['fixtures/organization/test.json']

    def test_quiz_list_status_code(self) -> None:
        """тестируем статус код страницы со списком квизов"""
        response = django.test.Client().get(django.urls.reverse('quiz:list'))
        self.assertEqual(response.status_code, 200)

    def test_quiz_list_context(self) -> None:
        """тестируем контекст страницы со списком квизов"""
        response = django.test.Client().get(django.urls.reverse('quiz:list'))
        self.assertIn('quizzes', response.context)

    def test_quiz_list_model(self) -> None:
        """тестируем модель на странице со списком квизов"""
        response = django.test.Client().get(django.urls.reverse('quiz:list'))
        self.assertTrue(
            all(
                map(
                    lambda x: isinstance(x, quiz.models.Quiz),
                    response.context['quizzes'],
                )
            )
        )

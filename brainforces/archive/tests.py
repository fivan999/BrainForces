import parameterized

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

    @parameterized.parameterized.expand(
        [
            ['1', '', 7],
            ['1', 'Имя', 2],
            ['1', 'имя', 2],
            ['1', 'льва', 1],
            ['2', 'фиван', 1],
            ['3', 'фиван', 2],
            ['1', 'la,rwfhkierjh,f', 0],
            ['2', 'dFQWED', 0],
            ['3', 'lwkerf', 0],
            ['4', 'ergf', 0],
        ]
    )
    def test_question_search(
        self, criteria: str, text: str, expected_num: int
    ) -> None:
        """тестируем количество записей приходящих по определенному запросу"""
        client = django.test.Client()
        response = client.get(
            django.urls.reverse('archive:archive'),
            data={'search_by': criteria, 'query': text},
        )
        self.assertEqual(len(response.context['questions']), expected_num)

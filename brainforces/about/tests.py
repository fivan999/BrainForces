import django.test
import django.urls


class AboutTests(django.test.TestCase):
    """тестируем приложение about"""

    def test_about_main_page_status_code(self) -> None:
        """тестируем главную страницу приложения about"""
        response = django.test.Client().get(django.urls.reverse('about:about'))
        self.assertEqual(response.status_code, 200)

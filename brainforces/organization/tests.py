import django.test

import django.urls

import organization.models

import users.models


class OrganizationTest(django.test.TestCase):
    """тестируем организации"""

    fixtures = ['fixtures/organization/test.json']

    def test_organizations_list_status_code(self) -> None:
        """тестируем статус код страницы с организациями"""
        us = users.models.User.objects.create(
            username='se;lrfnkeev',
            email='awefoaerruf@gmail.com',
        )
        us.set_password('password')
        us.save()
        print(us.password)
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
                    response.context['organizations']
                )
            )
        )

    def test_organization_main_page(self) -> None:
        """тестируем главную страницу организации"""

    def tearDown(self) -> None:
        """удаление тестовых данных"""
        users.models.User.objects.all().delete()
        organization.models.Organization.objects.all().delete()
        super().tearDown()

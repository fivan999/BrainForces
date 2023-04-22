import django.db.models
import django.views.generic

import organization.models

import django.conf


class HomeView(django.views.generic.ListView):
    """список постов на главной странице"""

    template_name = 'homepage/homepage.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self) -> django.db.models.QuerySet:
        """не показываем приватные викторины в общем списке"""
        print(django.conf.settings.DATABASES)
        return (
            organization.models.OrganizationPost.objects.filter(
                is_private=False
            )
            .select_related('posted_by')
            .only('name', 'text', 'posted_by__name')
        )

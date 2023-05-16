import django.db.models
import django.views.generic

import organization.models


class HomeView(django.views.generic.ListView):
    """список постов на главной странице"""

    template_name = 'homepage/homepage.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self) -> django.db.models.QuerySet:
        """не показываем приватные викторины в общем списке"""
        return organization.models.OrganizationPost.objects.filter_user_access(
            user_pk=self.request.user.pk
        )

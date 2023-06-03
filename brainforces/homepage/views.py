import django.contrib.postgres.search
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
        queryset = (
            organization.models.OrganizationPost.objects.filter_user_access(
                user_pk=self.request.user.pk
            ).order_by('-id')
        )
        query = self.request.GET.get('query')
        if query:
            search_vector = django.contrib.postgres.search.SearchVector(
                'name', 'text', 'posted_by__name'
            )
            search_query = django.contrib.postgres.search.SearchQuery(query)
            queryset = (
                queryset.annotate(
                    search=search_vector,
                    rank=django.contrib.postgres.search.SearchRank(
                        search_vector, search_query
                    ),
                )
                .filter(search=search_query)
                .order_by('-rank', '-id')
            )
        return queryset

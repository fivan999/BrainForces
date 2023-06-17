import django.db.models
import django.views.generic

import core.views
import organization.documents
import organization.models


class HomeView(core.views.ElasticSearchListView):
    """список постов на главной странице"""

    template_name = 'homepage/homepage.html'
    context_object_name = 'posts'
    paginate_by = 10
    document_class = organization.documents.OrganizationPostDocument
    search_fields = ['name', 'text']

    def get_default_queryset(self) -> django.db.models.QuerySet:
        return organization.models.OrganizationPost.objects.filter_user_access(
            user_pk=self.request.user.pk
        ).order_by('-id')

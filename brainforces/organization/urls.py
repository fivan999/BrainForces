import organization.views

import django.urls


app_name = 'organization'

urlpatterns = [
    django.urls.path(
        '<int:pk>/',
        organization.views.OrganizationMainView.as_view(),
        name='organization_profile',
    ),
    django.urls.path(
        '<int:pk>/users/',
        organization.views.OrganizationUsersView.as_view(),
        name='organization_users',
    ),
]

import django.urls

import archive.views


app_name = 'archive'

urlpatterns = [
    django.urls.path(
        '', archive.views.ArchiveQuestionsView.as_view(), name='archive'
    ),
]

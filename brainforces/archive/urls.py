import django.urls

import archive.views


app_name = 'archive'

urlpatterns = [
    django.urls.path('', archive.views.ArchiveView.as_view(), name='archive'),
    django.urls.path(
        'question/<int:pk>/',
        archive.views.ArchiveQuestionView.as_view(),
        name='question_detail',
    ),
]

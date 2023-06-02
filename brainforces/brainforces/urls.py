import django.conf
import django.conf.urls.static
import django.contrib.admin
import django.contrib.staticfiles.urls
import django.urls
import django.utils.timezone
import django.views.generic

import core.views


urlpatterns = [
    django.urls.path('', django.urls.include('homepage.urls')),
    django.urls.path('archive/', django.urls.include('archive.urls')),
    django.urls.path('admin/', django.contrib.admin.site.urls),
    django.urls.path('auth/', django.urls.include('users.urls')),
    django.urls.path('auth/', django.urls.include('django.contrib.auth.urls')),
    django.urls.path('quizzes/', django.urls.include('quiz.urls')),
    django.urls.path(
        'ckeditor/', django.urls.include('ckeditor_uploader.urls')
    ),
    django.urls.path(
        'organizations/', django.urls.include('organization.urls')
    ),
    django.urls.path('about/', django.urls.include('about.urls')),
    django.urls.path(
        'social-auth/',
        django.urls.include('social_django.urls', namespace='social_auth'),
    ),
]

handler404 = core.views.custom_404
handler500 = core.views.custom_500


if django.conf.settings.DEBUG:
    urlpatterns += (
        django.urls.path(
            '__debug__/', django.urls.include('debug_toolbar.urls')
        ),
    )
    if django.conf.settings.MEDIA_ROOT:
        urlpatterns += django.conf.urls.static.static(
            django.conf.settings.MEDIA_URL,
            document_root=django.conf.settings.MEDIA_ROOT,
        )
    else:
        urlpatterns += (
            django.contrib.staticfiles.urls.staticfiles_urlpatterns()
        )

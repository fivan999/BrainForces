import django.urls
import django.views.generic


app_name = 'about'

urlpatterns = [
    django.urls.path(
        '',
        django.views.generic.TemplateView.as_view(
            template_name='about/about.html'
        ),
        name='about',
    )
]

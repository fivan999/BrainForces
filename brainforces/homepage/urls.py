import django.urls
import django.views.generic


app_name = 'homepage'

urlpatterns = [
    django.urls.path(
        '',
        django.views.generic.TemplateView.as_view(
            template_name='homepage/homepage.html'
        ),
        name='homepage'
    )
]

import django.views.generic


class AboutView(django.views.generic.TemplateView):
    """страница о сайте"""

    template_name = 'about/about.html'

import about.views

import django.urls


app_name = 'about'

urlpatterns = [
    django.urls.path('', about.views.AboutView.as_view(), name='about')
]

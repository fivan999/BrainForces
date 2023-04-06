import django.urls

import homepage.views


app_name = 'homepage'

urlpatterns = [
    django.urls.path('', homepage.views.HomeView.as_view(), name='homepage'),
]

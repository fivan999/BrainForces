import django.contrib.sites
import django.urls


urlpatterns = [
    django.urls.path('admin/', django.contrib.sites.urls),
    django.urls.path('', django.urls.include('homepage.urls')),
]

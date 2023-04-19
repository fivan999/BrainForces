import django.views.generic

import users.models


class UsernameMixinView(django.views.generic.View):
    """дополняем контекст страниц именем пользователя"""

    def get_context_data(self, *args, **kwargs) -> dict:
        context = super().get_context_data(*args, **kwargs)
        user = django.shortcuts.get_object_or_404(
            users.models.User.objects.all().only('username'),
            pk=self.kwargs['pk'],
        )
        context['username'] = user.username
        return context

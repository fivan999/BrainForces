import django.contrib.admin
import django.contrib.auth.admin
import django.contrib.auth.models

import users.models


class ProfileAdmin(django.contrib.admin.TabularInline):
    """отображение профиля в админке"""

    model = users.models.Profile
    can_delete = False


class USerAdmin(django.contrib.auth.admin.UserAdmin):
    """отображение модели пользователя в админке"""

    inlines = (ProfileAdmin,)


django.contrib.admin.site.register(users.models.User, USerAdmin)

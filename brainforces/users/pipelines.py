import users.models


def create_profile_for_social_authenticated_user(
    backend, user: users.models.User, *args, **kwargs
) -> None:
    """
    создание профиля для пользователя,
    который вошел через социальную сеть
    """
    users.models.Profile.objects.get_or_create(user=user)

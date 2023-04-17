import organization.models
import quiz.models
import users.models


def user_can_access_quiz(
    quiz_obj: quiz.models.Quiz, user_obj: users.models.User
) -> bool:
    """может ли пользователь зайти в викторину"""
    org_to_user_manager = organization.models.OrganizationToUser.objects
    return not quiz_obj.is_private or (
        quiz_obj.is_private
        and (
            org_to_user_manager.get_organization_member(
                pk=quiz_obj.organized_by.pk, user_pk=user_obj.pk
            )
        )
    )

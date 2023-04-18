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


def make_quiz_results(quiz_obj: quiz.models.Quiz) -> None:
    """
    подводим итоги викторины
    изменяем рейтинг и место пользователя в викторине
    """
    quiz_results = list(
        quiz.models.QuizResults.objects.filter(quiz__pk=quiz_obj.pk)
        .select_related('user')
        .only('rating_before', 'rating_after', 'solved', 'user')
        .order_by('-solved')
    )
    add_rating = quiz_obj.is_rated and not quiz_obj.is_private
    cur_place = 1
    for result_ind in range(len(quiz_results)):
        if add_rating:
            profile_obj = users.models.Profile.objects.get(
                user__pk=quiz_results[result_ind].user.pk
            )
            profile_obj.rating = quiz_results[result_ind].rating_after
            profile_obj.save()
        if (
            result_ind != 0
            and quiz_results[result_ind].solved
            != quiz_results[result_ind - 1].solved
        ):
            cur_place += 1
        quiz_results[result_ind].place = cur_place
        quiz_results[result_ind].save()
    quiz_obj.is_ended = True
    quiz_obj.save()

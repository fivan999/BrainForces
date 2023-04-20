import organization.models
import quiz.models
import users.models


def user_can_access_quiz(
    quiz_obj: quiz.models.Quiz, user_obj: users.models.User
) -> bool:
    """
    может ли пользователь зайти в викторину
    она не приватная или пользователь участник
    проводящей организации
    """
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
    изменяем рейтинг пользователя,
    его место в топе участников викторины
    """
    quiz_results = list(
        quiz.models.QuizResults.objects.filter(quiz__pk=quiz_obj.pk)
        .select_related('user')
        .order_by('-solved')
    )
    add_rating = quiz_obj.is_rated and not quiz_obj.is_private
    cur_place = 1
    to_update_profiles, quiz_results_objects = list(), list()
    profile_objects = users.models.Profile.objects.filter(
        user__pk__in=(quiz_result.user.pk for quiz_result in quiz_results)
    )
    for result_ind in range(len(quiz_results)):
        if add_rating:
            profile_obj = profile_objects[result_ind]
            profile_obj.rating = quiz_results[result_ind].rating_after
            to_update_profiles.append(profile_obj)
        if (
            result_ind != 0
            and quiz_results[result_ind].solved
            != quiz_results[result_ind - 1].solved
        ):
            cur_place += 1
        quiz_results[result_ind].place = cur_place
        quiz_results_objects.append(quiz_results[result_ind])
    quiz_obj.is_ended = True
    quiz_obj.save()
    users.models.Profile.objects.bulk_update(to_update_profiles, ('rating',))
    quiz.models.QuizResults.objects.bulk_update(
        quiz_results_objects, ('place',)
    )

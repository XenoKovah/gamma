from typing import Type

import pytest
from django.core.management import call_command

from core.tests.utils.helpers import load_params_from_json
from leaderboard import usecases
from leaderboard.dataclasses import LeaderboardRetrievingContext
from leaderboard.entity import LeaderboardMember
from leaderboard.repository import ORMLeaderboardMemberDataRepository, RedisLeaderboardRepository
from users.factories import GammaUserCoursePointsFactory, GammaUserFactory


class TestGetPersonalizedLeaderboardUseCase:
    @pytest.mark.django_db
    @pytest.mark.parametrize(
        "entry",
        load_params_from_json("leaderboard/tests/resources/personalized_leaderboard_cases.json"),
    )
    def test_correct_leaderboard_data_is_collected(
        self,
        entry: dict,
        gamma_user_factory: Type[GammaUserFactory],
    ) -> None:
        user_uid = entry["user_uid"]
        user_signup_source = entry["signup_source"]
        redis_leaderboard_repository = RedisLeaderboardRepository()
        leaderboard_member_data_repository = ORMLeaderboardMemberDataRepository()
        leaderboard_retrieving_context = LeaderboardRetrievingContext(user_uid, user_signup_source, None)

        for i in range(1, 31):
            gamma_user_factory(user_uid=f"user_uid_{i}", signup_source=user_signup_source, points=31 - i)

        call_command("initialize_leaderboard")

        top10_members_data, competitors_data, rank = usecases.GetPersonalizedLeaderboardUseCase(
            redis_leaderboard_repository,
            leaderboard_member_data_repository,
        ).execute(leaderboard_retrieving_context)

        assert rank == entry["expected_rank"]
        assert top10_members_data == entry["expected_top10"]
        assert competitors_data == entry["expected_competitors"]

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        "entry",
        load_params_from_json("leaderboard/tests/resources/leaderboard_with_signup_source_cases.json"),
    )
    def test_correct_leaderboard_data_is_collected_according_to_signup_source(
        self,
        entry: dict,
        gamma_user_factory: Type[GammaUserFactory],
    ) -> None:
        user_uid = entry["user_uid"]
        signup_source = entry["signup_source"]
        redis_leaderboard_repository = RedisLeaderboardRepository()
        leaderboard_member_data_repository = ORMLeaderboardMemberDataRepository()
        leaderboard_retrieving_context = LeaderboardRetrievingContext(user_uid, signup_source[1], None)

        # Odd users are created with signup_source = "RG", even - signup_source = "main"
        for i in range(1, 31):
            user_signup_source = signup_source[i % 2]
            gamma_user_factory(user_uid=f"user_uid_{i}", signup_source=user_signup_source, points=31 - i)

        call_command("initialize_leaderboard")

        top10_members_data, competitors_data, rank = usecases.GetPersonalizedLeaderboardUseCase(
            redis_leaderboard_repository,
            leaderboard_member_data_repository,
        ).execute(leaderboard_retrieving_context)

        assert rank == entry["expected_rank"]
        assert top10_members_data == entry["expected_top10"]
        assert competitors_data == entry["expected_competitors"]

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        "entry",
        load_params_from_json("leaderboard/tests/resources/leaderboard_cases_with_same_points.json"),
    )
    def test_correct_leaderboard_data_is_collected_for_user_with_same_points(
        self,
        entry: dict,
        gamma_user_factory: Type[GammaUserFactory],
    ) -> None:
        all_users = entry["all_users"]
        user_uid = entry["user_uid"]
        signup_source = entry["signup_source"]
        redis_leaderboard_repository = RedisLeaderboardRepository()
        leaderboard_member_data_repository = ORMLeaderboardMemberDataRepository()
        leaderboard_retrieving_context = LeaderboardRetrievingContext(user_uid, signup_source, None)

        for item in all_users:
            gamma_user_factory(user_uid=item["user_uid"], signup_source=signup_source, points=item["points"])

        call_command("initialize_leaderboard")

        top10_members_data, competitors_data, rank = usecases.GetPersonalizedLeaderboardUseCase(
            redis_leaderboard_repository,
            leaderboard_member_data_repository,
        ).execute(leaderboard_retrieving_context)

        assert rank == entry["expected_rank"]
        assert top10_members_data == entry["expected_top10"]
        assert competitors_data == entry["expected_competitors"]

    @pytest.mark.django_db
    def test_correct_incomplete_top10_members_data_is_collected_when_current_user_has_no_points(
        self,
        gamma_user_factory: Type[GammaUserFactory],
    ) -> None:
        redis_leaderboard_repository = RedisLeaderboardRepository()
        leaderboard_member_data_repository = ORMLeaderboardMemberDataRepository()
        usecase = usecases.GetPersonalizedLeaderboardUseCase(
            redis_leaderboard_repository,
            leaderboard_member_data_repository,
        )
        current_user = LeaderboardMember({"user_uid": "user_uid", "points": 0})
        leaderboard_retrieving_context = LeaderboardRetrievingContext(current_user.user_uid, "main", None)

        for i in range(1, 3):
            gamma_user_factory(user_uid=f"user_uid_{i}", points=3 - i)
        gamma_user_factory(user_uid=current_user.user_uid, points=current_user.points)

        call_command("initialize_leaderboard")

        top10_members_data = usecase._get_top10_members_data(current_user, 3, leaderboard_retrieving_context)

        assert len(top10_members_data) == 2
        assert top10_members_data[0]["user_uid"] == "user_uid_1"
        assert top10_members_data[1]["user_uid"] == "user_uid_2"

    @pytest.mark.django_db
    def test_correct_top10_members_data_is_collected_when_current_user_has_rank_10(
        self,
        gamma_user_factory: Type[GammaUserFactory],
    ) -> None:
        redis_leaderboard_repository = RedisLeaderboardRepository()
        leaderboard_member_data_repository = ORMLeaderboardMemberDataRepository()
        usecase = usecases.GetPersonalizedLeaderboardUseCase(
            redis_leaderboard_repository,
            leaderboard_member_data_repository,
        )
        current_user_uid = "current_user"
        current_user = LeaderboardMember({"user_uid": current_user_uid, "points": 1})
        leaderboard_retrieving_context = LeaderboardRetrievingContext(current_user.user_uid, "main", None)

        for i in range(1, 10):
            gamma_user_factory(user_uid=f"user_uid_{i}", points=11 - i)
        gamma_user_factory(user_uid=current_user.user_uid, points=current_user.points)

        call_command("initialize_leaderboard")

        top10_members_data = usecase._get_top10_members_data(current_user, 10, leaderboard_retrieving_context)

        assert len(top10_members_data) == 10
        assert top10_members_data[9]["user_uid"] == current_user_uid

    @pytest.mark.django_db
    def test_empty_top10_members_data_is_collected_when_current_user_is_only_one_and_has_0_score(
        self,
        gamma_user_factory: Type[GammaUserFactory],
    ) -> None:
        redis_leaderboard_repository = RedisLeaderboardRepository()
        leaderboard_member_data_repository = ORMLeaderboardMemberDataRepository()
        usecase = usecases.GetPersonalizedLeaderboardUseCase(
            redis_leaderboard_repository,
            leaderboard_member_data_repository,
        )
        current_user = LeaderboardMember({"user_uid": "current_user", "points": 0})
        leaderboard_retrieving_context = LeaderboardRetrievingContext(current_user.user_uid, "main", None)

        gamma_user_factory(user_uid=current_user.user_uid, points=current_user.points)

        call_command("initialize_leaderboard")

        top10_members_data = usecase._get_top10_members_data(current_user, 10, leaderboard_retrieving_context)

        assert len(top10_members_data) == 0

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        "entry",
        load_params_from_json("leaderboard/tests/resources/cases_tail_competitors.json"),
    )
    def test_collected_tail_competitors_has_correct_length(
        self,
        entry: dict,
        gamma_user_factory: Type[GammaUserFactory],
    ) -> None:
        redis_leaderboard_repository = RedisLeaderboardRepository()
        leaderboard_member_data_repository = ORMLeaderboardMemberDataRepository()
        usecase = usecases.GetPersonalizedLeaderboardUseCase(
            redis_leaderboard_repository,
            leaderboard_member_data_repository,
        )
        current_user = LeaderboardMember({"user_uid": "current_user", "points": entry["points"]})

        for i in range(30):
            gamma_user_factory(points=31 - i)
        gamma_user_factory(user_uid=current_user.user_uid, points=current_user.points)

        call_command("initialize_leaderboard")

        tail_competitors = usecase._get_tail_competitors(current_user, "leaderboard:main")

        assert len(tail_competitors) == entry["expected_length"]


class TestRemoveUserFromLeaderboardsUseCase:
    @pytest.mark.django_db
    def test_user_is_removed_from_general_leaderboard(
        self,
        gamma_user_factory: Type[GammaUserFactory],
    ) -> None:
        user_uid = "test_user"
        signup_source = "main"
        gamma_user_factory(user_uid=user_uid, signup_source=signup_source, points=100)

        call_command("initialize_leaderboard")

        repository = RedisLeaderboardRepository()
        assert repository.get_or_init_user_score(user_uid, "leaderboard:main") == 100.0

        usecases.RemoveUserFromLeaderboardsUseCase(repository).execute(
            user_uid, signup_source, []
        )

        # After removal, user should not exist in leaderboard (re-init sets score to 0)
        assert repository.get_or_init_user_score(user_uid, "leaderboard:main") == 0.0

    @pytest.mark.django_db
    def test_user_is_removed_from_course_leaderboards(
        self,
        gamma_user_factory: Type[GammaUserFactory],
        gamma_user_course_points_factory: Type[GammaUserCoursePointsFactory],
    ) -> None:
        user_uid = "test_user"
        signup_source = "main"
        gamma_user = gamma_user_factory(user_uid=user_uid, signup_source=signup_source, points=100)
        gamma_user_course_points_factory(gamma_user=gamma_user, course_id="course-1", points=50)
        gamma_user_course_points_factory(gamma_user=gamma_user, course_id="course-2", points=30)

        call_command("initialize_leaderboard")

        repository = RedisLeaderboardRepository()
        assert repository.get_or_init_user_score(user_uid, "leaderboard:main:course-1") == 50.0
        assert repository.get_or_init_user_score(user_uid, "leaderboard:main:course-2") == 30.0

        usecases.RemoveUserFromLeaderboardsUseCase(repository).execute(
            user_uid, signup_source, ["course-1", "course-2"]
        )

        # After removal, user should not exist in course leaderboards
        assert repository.get_or_init_user_score(user_uid, "leaderboard:main:course-1") == 0.0
        assert repository.get_or_init_user_score(user_uid, "leaderboard:main:course-2") == 0.0

    @pytest.mark.django_db
    def test_user_without_signup_source_is_removed_from_main_leaderboard(
        self,
        gamma_user_factory: Type[GammaUserFactory],
    ) -> None:
        user_uid = "test_user"
        gamma_user_factory(user_uid=user_uid, signup_source=None, points=100)

        call_command("initialize_leaderboard")

        repository = RedisLeaderboardRepository()
        assert repository.get_or_init_user_score(user_uid, "leaderboard:main") == 100.0

        # When signup_source is None, should fall back to main
        usecases.RemoveUserFromLeaderboardsUseCase(repository).execute(
            user_uid, None, []
        )

        assert repository.get_or_init_user_score(user_uid, "leaderboard:main") == 0.0

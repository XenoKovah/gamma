from typing import List, Set, Type
from unittest.mock import MagicMock, patch

import pytest
from redis import Redis

from core.tests.utils.helpers import load_params_from_json
from leaderboard import tasks
from leaderboard.repository import RedisLeaderboardRepository, RedisLeaderboardsPendingUpdateRepository
from users.models import GammaUser
from users.factories import GammaUserCoursePointsFactory, GammaUserFactory


pytestmark = pytest.mark.django_db


class TestTaskInitializeLeaderboards:
    @patch("leaderboard.tasks.usecases.InitializeLeaderboardsUseCase")
    @patch("leaderboard.tasks.repository.ORMLeaderboardMemberDataRepository")
    @patch("leaderboard.tasks.repository.RedisLeaderboardRepository")
    def test_initialize_leaderboards_use_case_is_executed(
        self,
        redis_leaderboard_repository_mock: MagicMock,
        orm_leaderboard_member_data_repository_mock: MagicMock,
        initialize_leaderboards_use_case_mock: MagicMock,
    ) -> None:
        offset = 200
        batch_size = 100

        tasks.task_initialize_leaderboards(offset, batch_size)

        redis_leaderboard_repository_mock.assert_called_once_with()
        orm_leaderboard_member_data_repository_mock.assert_called_once_with()
        initialize_leaderboards_use_case_mock.assert_called_once_with(
            redis_leaderboard_repository_mock.return_value,
            orm_leaderboard_member_data_repository_mock.return_value,
        )

        initialize_leaderboards_use_case_mock.return_value.execute.assert_called_once_with(offset, batch_size)

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        "entry",
        load_params_from_json("leaderboard/tests/resources/leaderboard_initialization_cases.json"),
    )
    def test_user_leaderboard_score_is_correctly_initialized(
        self,
        gamma_user_factory: Type[GammaUserFactory],
        gamma_user_course_points_factory: Type[GammaUserCoursePointsFactory],
        entry: dict,
    ) -> None:
        for user_data in entry["gamma_users"]:
            gamma_user = gamma_user_factory(
                user_uid=user_data["user_uid"],
                points=user_data["points"],
                signup_source=user_data["signup_source"],
            )
            for course_id, points in user_data["course_points"].items():
                gamma_user_course_points_factory(gamma_user=gamma_user, course_id=course_id, points=points)

        repository = RedisLeaderboardRepository()

        tasks.task_initialize_leaderboards(entry["offset"], entry["batch_size"])

        for data_item in entry["user_leaderboard_scores"]:
            assert repository.get_or_init_user_score(
                data_item["user_uid"],
                data_item["leaderboard_id"],
            ) == data_item["score"]

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        "users_count,offset,batch_size,batches_left_before,batches_left_after",
        (
            (77, 40, 10, 5, 4),
            (12, 3, 0, 4, 3),
            (19, 0, 100, 1, 0),
        ),
    )
    def test_batches_left_is_decremented_after_batch_initialization(
        self,
        gamma_user_factory: Type[GammaUserFactory],
        redis_client: Redis,
        users_count: int,
        offset: int,
        batch_size: int,
        batches_left_before: int,
        batches_left_after: int,
    ) -> None:
        for _ in range(users_count):
            gamma_user_factory()
        redis_client.set("leaderboards_initialization_batches_left", batches_left_before)

        tasks.task_initialize_leaderboards(offset, batch_size)

        assert int(redis_client.get("leaderboards_initialization_batches_left")) == batches_left_after


class TestTaskEnqueueLeaderboardsUserDataUpdate:
    @patch("leaderboard.tasks.usecases.EnqueueLeaderboardsUpdateUseCase")
    @patch("leaderboard.tasks.repository.RedisLeaderboardsPendingUpdateRepository")
    def test_enqueue_leaderboards_update_use_case_is_executed(
        self,
        redis_leaderboard_pending_update_repository_mock: MagicMock,
        enqueue_leaderboards_update_use_case_mock: MagicMock,
    ) -> None:
        user_uid = "test_user"

        tasks.task_enqueue_leaderboards_user_data_update(user_uid)

        redis_leaderboard_pending_update_repository_mock.assert_called_once_with()
        enqueue_leaderboards_update_use_case_mock.assert_called_once_with(
            redis_leaderboard_pending_update_repository_mock.return_value,
        )
        enqueue_leaderboards_update_use_case_mock.return_value.execute.assert_called_once_with(user_uid)

    @pytest.mark.parametrize(
        "task_call_args,expected_users_with_scheduled_update",
        (
            ([], set()),
            (["user_1"], {"user_1"}),
            (["user_1", "user_1", "user_1"], {"user_1"}),
            (
                ["user_1", "user_2", "user_3", "user_4", "user_5"],
                {"user_1", "user_2", "user_3", "user_4", "user_5"},
            ),
            (
                ["user_5", "user_2", "user_1", "user_3", "user_4", "user_5", "user_3"],
                {"user_1", "user_2", "user_3", "user_4", "user_5"},
            ),
        )
    )
    def test_user_leaderboards_update_is_scheduled_if_leaderboards_are_initialized(
        self,
        redis_client: Redis,
        task_call_args: List[str],
        expected_users_with_scheduled_update: Set[str],
    ) -> None:
        redis_client.set("leaderboards_initialization_batches_left", 0)
        repository = RedisLeaderboardsPendingUpdateRepository()

        for arg in task_call_args:
            tasks.task_enqueue_leaderboards_user_data_update(arg)

        assert repository.pop_users_with_pending_leaderboards_update() == expected_users_with_scheduled_update

    @pytest.mark.parametrize(
        "task_call_args",
        ([], ["user_1"], ["user_1", "user_2", "user_3"], ["user_3", "user_1", "user_1", "user_2", "user_3"]),
    )
    def test_user_leaderboards_update_is_not_scheduled_if_leaderboards_are_not_initialized(
        self,
        task_call_args: List[str],
    ) -> None:
        repository = RedisLeaderboardsPendingUpdateRepository()

        for arg in task_call_args:
            tasks.task_enqueue_leaderboards_user_data_update(arg)

        assert repository.pop_users_with_pending_leaderboards_update() == set()


class TestTaskUpdateLeaderboards:
    @patch("leaderboard.tasks.usecases.UpdateLeaderboardsUseCase")
    @patch("leaderboard.tasks.repository.RedisLeaderboardsPendingUpdateRepository")
    @patch("leaderboard.tasks.repository.ORMLeaderboardMemberDataRepository")
    @patch("leaderboard.tasks.repository.RedisLeaderboardRepository")
    def test_update_leaderboards_use_case_is_executed(
        self,
        redis_leaderboard_repository_mock: MagicMock,
        orm_leaderboard_member_data_repository_mock: MagicMock,
        redis_leaderboards_pending_update_repository_mock: MagicMock,
        update_leaderboards_use_case_mock: MagicMock,
    ) -> None:
        tasks.task_update_leaderboards()

        redis_leaderboard_repository_mock.assert_called_once_with()
        orm_leaderboard_member_data_repository_mock.assert_called_once_with()
        redis_leaderboards_pending_update_repository_mock.assert_called_once_with()
        update_leaderboards_use_case_mock.assert_called_once_with(
            redis_leaderboard_repository_mock.return_value,
            orm_leaderboard_member_data_repository_mock.return_value,
            redis_leaderboards_pending_update_repository_mock.return_value,
        )
        update_leaderboards_use_case_mock.return_value.execute.assert_called_once_with()

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        "entry",
        load_params_from_json("leaderboard/tests/resources/leaderboard_updating_cases.json"),
    )
    def test_user_leaderboard_score_is_correctly_updated(
        self,
        gamma_user_factory: Type[GammaUserFactory],
        gamma_user_course_points_factory: Type[GammaUserCoursePointsFactory],
        entry: dict,
    ) -> None:
        gamma_users = entry["gamma_users_initial_state"]

        for user_data in gamma_users:
            gamma_user = gamma_user_factory(
                user_uid=user_data["user_uid"],
                points=user_data["points"],
                signup_source=user_data["signup_source"],
            )
            for course_id, points in user_data["course_points"].items():
                gamma_user_course_points_factory(gamma_user=gamma_user, course_id=course_id, points=points)

        tasks.task_initialize_leaderboards(0, len(gamma_users))

        for user_updates in entry["gamma_users_updates"]:
            user = GammaUser.objects.get(user_uid=user_updates["user_uid"])
            user.points = user_updates["points"]
            user.save(update_fields=["points"])

            for course_id, points in user_updates["course_points"].items():
                user_courses_points = user.courses_points.get(course_id=course_id)
                user_courses_points.points = points
                user_courses_points.save(update_fields=["points"])

        leaderboards_pending_update_repository = RedisLeaderboardsPendingUpdateRepository()
        leaderboard_repository = RedisLeaderboardRepository()

        for user_uid in entry["users_to_update_leaderboards"]:
            leaderboards_pending_update_repository.schedule_user_leaderboards_update(user_uid)

        tasks.task_update_leaderboards()

        for data_item in entry["user_leaderboard_scores"]:
            assert leaderboard_repository.get_or_init_user_score(
                data_item["user_uid"],
                data_item["leaderboard_id"],
            ) == data_item["score"]


class TestTaskRemoveUserFromLeaderboards:
    @patch("leaderboard.tasks.usecases.RemoveUserFromLeaderboardsUseCase")
    @patch("leaderboard.tasks.repository.RedisLeaderboardRepository")
    def test_remove_user_from_leaderboards_use_case_is_executed(
        self,
        redis_leaderboard_repository_mock: MagicMock,
        remove_user_from_leaderboards_use_case_mock: MagicMock,
    ) -> None:
        user_uid = "test_user"
        signup_source = "main"
        course_ids = ["course-1", "course-2"]

        tasks.task_remove_user_from_leaderboards(user_uid, signup_source, course_ids)

        redis_leaderboard_repository_mock.assert_called_once_with()
        remove_user_from_leaderboards_use_case_mock.assert_called_once_with(
            redis_leaderboard_repository_mock.return_value,
        )
        remove_user_from_leaderboards_use_case_mock.return_value.execute.assert_called_once_with(
            user_uid,
            signup_source,
            course_ids,
        )

    def test_user_is_removed_from_general_leaderboard(
        self,
        gamma_user_factory: Type[GammaUserFactory],
    ) -> None:
        user_uid = "test_user"
        signup_source = "main"
        gamma_user_factory(user_uid=user_uid, signup_source=signup_source, points=100)

        tasks.task_initialize_leaderboards(0, 10)

        repository = RedisLeaderboardRepository()
        assert repository.get_or_init_user_score(user_uid, "leaderboard:main") == 100.0

        tasks.task_remove_user_from_leaderboards(user_uid, signup_source, [])

        # After removal, user should not exist in leaderboard (re-init sets score to 0)
        assert repository.get_or_init_user_score(user_uid, "leaderboard:main") == 0.0

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

        tasks.task_initialize_leaderboards(0, 10)

        repository = RedisLeaderboardRepository()
        assert repository.get_or_init_user_score(user_uid, "leaderboard:main:course-1") == 50.0
        assert repository.get_or_init_user_score(user_uid, "leaderboard:main:course-2") == 30.0

        tasks.task_remove_user_from_leaderboards(user_uid, signup_source, ["course-1", "course-2"])

        # After removal, user should not exist in leaderboards (re-init sets score to 0)
        assert repository.get_or_init_user_score(user_uid, "leaderboard:main:course-1") == 0.0
        assert repository.get_or_init_user_score(user_uid, "leaderboard:main:course-2") == 0.0

    def test_user_without_signup_source_is_removed_from_main_leaderboard(
        self,
        gamma_user_factory: Type[GammaUserFactory],
    ) -> None:
        user_uid = "test_user"
        gamma_user_factory(user_uid=user_uid, signup_source=None, points=100)

        tasks.task_initialize_leaderboards(0, 10)

        repository = RedisLeaderboardRepository()
        assert repository.get_or_init_user_score(user_uid, "leaderboard:main") == 100.0

        tasks.task_remove_user_from_leaderboards(user_uid, None, [])

        assert repository.get_or_init_user_score(user_uid, "leaderboard:main") == 0.0

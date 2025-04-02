from typing import List, Set, Type
from unittest.mock import MagicMock, patch

import pytest
from redis import Redis

from leaderboard import tasks
from leaderboard.repository import RedisLeaderboardRepository, RedisLeaderboardsPendingUpdateRepository
from users.factories import GammaUserFactory


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
        "user_uid,leaderboard_id,expected_score",
        (
            ("test_user_1", "leaderboard:RG", 0),
            ("test_user_1", "leaderboard:main", 0),
            ("test_user_2", "leaderboard:RG", 0),
            ("test_user_2", "leaderboard:main", 0),
            ("test_user_3", "leaderboard:RG", 7),
            ("test_user_3", "leaderboard:main", 0),
            ("test_user_4", "leaderboard:RG", 0),
            ("test_user_4", "leaderboard:main", 1),
            ("test_user_5", "leaderboard:RG", 0),
            ("test_user_5", "leaderboard:main", 0),
        ),
    )
    def test_user_leaderboard_score_is_correctly_initialized(
        self,
        gamma_user_factory: Type[GammaUserFactory],
        user_uid: str,
        leaderboard_id: str,
        expected_score: int,
    ) -> None:
        gamma_user_factory(user_uid="test_user_1", points=6, signup_source="main")
        gamma_user_factory(user_uid="test_user_2", points=0, signup_source="main")
        gamma_user_factory(user_uid="test_user_3", points=7, signup_source="RG")
        gamma_user_factory(user_uid="test_user_4", points=1, signup_source="main")
        gamma_user_factory(user_uid="test_user_5", points=15, signup_source="RG")
        repository = RedisLeaderboardRepository()

        tasks.task_initialize_leaderboards(2, 2)

        assert repository.get_or_init_user_score(user_uid, leaderboard_id) == expected_score

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
    def test_user_leaderboards_update_is_scheduled_if_leaderboards_updating_is_allowed(
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
    def test_user_leaderboards_update_is_not_scheduled_if_leaderboards_updating_is_not_allowed(
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
        "user_uid,leaderboard_id,expected_score",
        (
            ("test_user_1", "leaderboard:RG", 0),
            ("test_user_1", "leaderboard:main", 6),
            ("test_user_2", "leaderboard:RG", 0),
            ("test_user_2", "leaderboard:main", 0),
            ("test_user_3", "leaderboard:RG", 7),
            ("test_user_3", "leaderboard:main", 0),
        ),
    )
    def test_user_leaderboard_score_is_correctly_updated(
        self,
        gamma_user_factory: Type[GammaUserFactory],
        redis_client: Redis,
        user_uid: str,
        leaderboard_id: str,
        expected_score: int,
    ) -> None:
        gamma_user_factory(user_uid="test_user_1", points=6, signup_source="main")
        gamma_user_factory(user_uid="test_user_2", points=3, signup_source="main")
        gamma_user_factory(user_uid="test_user_3", points=7, signup_source="RG")
        redis_client.set("leaderboards_initialization_batches_left", 0)
        leaderboards_pending_update_repository = RedisLeaderboardsPendingUpdateRepository()
        leaderboards_pending_update_repository.schedule_user_leaderboards_update("test_user_1")
        leaderboards_pending_update_repository.schedule_user_leaderboards_update("test_user_3")
        leaderboard_repository = RedisLeaderboardRepository()

        tasks.task_update_leaderboards()

        assert leaderboard_repository.get_or_init_user_score(user_uid, leaderboard_id) == expected_score

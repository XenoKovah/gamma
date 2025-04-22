from typing import Type
from unittest.mock import MagicMock, patch

import pytest
from django.core.management import call_command
from redis import Redis

from leaderboard.management.commands.initialize_leaderboard import Command
from leaderboard.repository import RedisLeaderboardRepository
from users.factories import GammaUserFactory


pytestmark = pytest.mark.django_db


@patch("leaderboard.management.commands.initialize_leaderboard.ScheduleLeaderboardsInitializationUseCase")
@patch("leaderboard.management.commands.initialize_leaderboard.ORMLeaderboardMemberDataRepository")
def test_handle_executes_schedule_leaderboards_initialization_use_case(
    orm_leaderboard_member_data_repository_mock: MagicMock,
    schedule_leaderboards_initialization_use_case_mock: MagicMock,
) -> None:
    command = Command()

    command.handle()

    orm_leaderboard_member_data_repository_mock.assert_called_once_with()
    schedule_leaderboards_initialization_use_case_mock.assert_called_once_with(
        orm_leaderboard_member_data_repository_mock.return_value
    )
    schedule_leaderboards_initialization_use_case_mock.return_value.execute.assert_called_once_with(100)


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
        ("test_user_4", "leaderboard:RG", 0),
        ("test_user_4", "leaderboard:main", 1),
        ("test_user_5", "leaderboard:RG", 15),
        ("test_user_5", "leaderboard:main", 0),
    ),
)
def test_user_score_is_correct_after_leaderboards_initialization(
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

    call_command("initialize_leaderboard")

    assert repository.get_or_init_user_score(user_uid, leaderboard_id) == expected_score


@pytest.mark.django_db
@pytest.mark.parametrize("leaderboards_initialization_batches_left", (1, 2, 10, 100))
def test_leaderboards_initialization_is_not_scheduled_if_it_is_in_progress(
    gamma_user_factory: Type[GammaUserFactory],
    redis_client: Redis,
    leaderboards_initialization_batches_left: int,
) -> None:
    user_uid = "test_user_1"
    leaderboard_id = "leaderboard:main"
    gamma_user_factory(user_uid=user_uid, points=6, signup_source="main")
    redis_client.set("leaderboards_initialization_batches_left", leaderboards_initialization_batches_left)
    repository = RedisLeaderboardRepository()

    call_command("initialize_leaderboard")

    assert repository.get_or_init_user_score(user_uid, leaderboard_id) == 0

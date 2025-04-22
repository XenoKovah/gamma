import pytest

from unittest.mock import MagicMock, patch

from django.core.management import call_command
from redis import Redis

from leaderboard.management.commands.reset_leaderboards_initialization_status import Command


pytestmark = pytest.mark.django_db


@patch(
    "leaderboard.management.commands.reset_leaderboards_initialization_status"
    ".ResetLeaderboardsInitializationStatusUseCase"
)
def test_handle_executes_reset_leaderboards_initialization_status_use_case(
    reset_leaderboards_initialization_status_use_case_mock: MagicMock,
) -> None:
    command = Command()

    command.handle()

    reset_leaderboards_initialization_status_use_case_mock.assert_called_once_with()
    reset_leaderboards_initialization_status_use_case_mock.return_value.execute.assert_called_once_with()


def test_leaderboards_initialization_batches_left_is_reset(redis_client: Redis) -> None:
    redis_client.set("leaderboards_initialization_batches_left", 100)

    call_command("reset_leaderboards_initialization_status")

    assert redis_client.get("leaderboards_initialization_batches_left") is None

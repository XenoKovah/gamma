from typing import Type
from unittest.mock import MagicMock, patch

import pytest
from django.db import transaction

from users.factories import GammaUserFactory


class TestLeaderboardsUserDataUpdateEnqueuing:
    @pytest.mark.django_db(transaction=True)
    @patch("leaderboard.tasks.task_enqueue_leaderboards_user_data_update")
    def test_update_task_is_scheduled_if_user_creation_transaction_is_committed(
        self,
        task_enqueue_leaderboards_user_data_update_mock: MagicMock,
        gamma_user_factory: Type[GammaUserFactory],
    ) -> None:
        user_uid = "test_user"

        with transaction.atomic():
            gamma_user_factory(user_uid=user_uid)

        task_enqueue_leaderboards_user_data_update_mock.delay.assert_called_once_with(user_uid)

    @pytest.mark.django_db(transaction=True)
    @patch("leaderboard.tasks.task_enqueue_leaderboards_user_data_update")
    def test_update_task_is_not_scheduled_if_user_creation_transaction_is_not_committed(
        self,
        task_enqueue_leaderboards_user_data_update_mock: MagicMock,
        gamma_user_factory: Type[GammaUserFactory],
    ) -> None:
        with transaction.atomic():
            gamma_user_factory(user_uid="test_user")

            task_enqueue_leaderboards_user_data_update_mock.delay.assert_not_called()

    @pytest.mark.django_db(transaction=True)
    @patch("leaderboard.tasks.task_enqueue_leaderboards_user_data_update")
    def test_update_task_is_scheduled_if_user_points_changing_is_committed(
        self,
        task_enqueue_leaderboards_user_data_update_mock: MagicMock,
        gamma_user_factory: Type[GammaUserFactory],
    ) -> None:
        user_uid = "test_user"
        gamma_user = gamma_user_factory(user_uid=user_uid)
        task_enqueue_leaderboards_user_data_update_mock.delay.reset_mock()

        with transaction.atomic():
            gamma_user.points += 5
            gamma_user.save(update_fields=("points",))

        task_enqueue_leaderboards_user_data_update_mock.delay.assert_called_once_with(user_uid)

    @pytest.mark.django_db(transaction=True)
    @patch("leaderboard.tasks.task_enqueue_leaderboards_user_data_update")
    def test_update_task_is_not_scheduled_if_user_points_changing_is_not_committed(
        self,
        task_enqueue_leaderboards_user_data_update_mock: MagicMock,
        gamma_user_factory: Type[GammaUserFactory],
    ) -> None:
        gamma_user = gamma_user_factory(user_uid="test_user")
        task_enqueue_leaderboards_user_data_update_mock.delay.reset_mock()

        with transaction.atomic():
            gamma_user.points += 5
            gamma_user.save(update_fields=("points",))

            task_enqueue_leaderboards_user_data_update_mock.delay.assert_not_called()

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.parametrize(
        "field,initial_value,updated_value",
        (
            (
                "chart",
                "{}",
                '{"chart.edx_bookmark_added": {"title": "Bookmark added", "points": 2}}',
            ),
            (
                "progress",
                "{}",
                '{"progress.2025": {"2025.03.21": 2}, "progress.2025.points": 2}'
            ),
        ),
    )
    @patch("leaderboard.tasks.task_enqueue_leaderboards_user_data_update")
    def test_update_task_is_not_scheduled_if_not_points_user_field_changing_is_committed(
        self,
        task_enqueue_leaderboards_user_data_update_mock: MagicMock,
        gamma_user_factory: Type[GammaUserFactory],
        field: str,
        initial_value: str,
        updated_value: str,
    ) -> None:
        user_init_options = {"user_uid": "test_user", field: initial_value}
        gamma_user = gamma_user_factory(**user_init_options)
        task_enqueue_leaderboards_user_data_update_mock.delay.reset_mock()

        with transaction.atomic():
            setattr(gamma_user, field, updated_value)
            gamma_user.save(update_fields=(field,))

        task_enqueue_leaderboards_user_data_update_mock.delay.assert_not_called()

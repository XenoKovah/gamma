from typing import Type
from unittest.mock import MagicMock, patch

import pytest
from django.db import transaction

from leaderboard.enums import LeaderboardsInitializationStatus
from leaderboard.handlers import _safe_enqueue_leaderboard_update
from users.factories import GammaUserFactory, GammaUserCoursePointsFactory


class TestSafeEnqueueLeaderboardUpdate:
    @pytest.mark.django_db
    @patch("leaderboard.handlers.tasks.task_enqueue_leaderboards_user_data_update")
    def test_dispatches_celery_task_on_success(self, mock_task: MagicMock) -> None:
        _safe_enqueue_leaderboard_update("user-1")
        mock_task.delay.assert_called_once_with("user-1")

    @pytest.mark.django_db
    @patch("leaderboard.handlers.tasks.task_enqueue_leaderboards_user_data_update")
    @patch("leaderboard.repository.RedisLeaderboardsPendingUpdateRepository.schedule_user_leaderboards_update")
    @patch(
        "leaderboard.utils.get_leaderboards_initialization_status",
        return_value=LeaderboardsInitializationStatus.COMPLETED,
    )
    def test_falls_back_to_direct_redis_write_on_celery_failure(
        self,
        mock_status: MagicMock,
        mock_schedule: MagicMock,
        mock_task: MagicMock,
    ) -> None:
        mock_task.delay.side_effect = ConnectionError("Redis broker down")

        _safe_enqueue_leaderboard_update("user-1")

        mock_schedule.assert_called_once_with("user-1")

    @pytest.mark.django_db
    @patch("leaderboard.handlers.tasks.task_enqueue_leaderboards_user_data_update")
    @patch("leaderboard.repository.RedisLeaderboardsPendingUpdateRepository.schedule_user_leaderboards_update")
    @patch(
        "leaderboard.utils.get_leaderboards_initialization_status",
        return_value=LeaderboardsInitializationStatus.IN_PROGRESS,
    )
    def test_skips_fallback_when_initialization_not_completed(
        self,
        mock_status: MagicMock,
        mock_schedule: MagicMock,
        mock_task: MagicMock,
    ) -> None:
        mock_task.delay.side_effect = ConnectionError("Redis broker down")

        _safe_enqueue_leaderboard_update("user-1")

        mock_schedule.assert_not_called()

    @pytest.mark.django_db
    @patch("leaderboard.handlers.tasks.task_enqueue_leaderboards_user_data_update")
    @patch("leaderboard.repository.RedisLeaderboardsPendingUpdateRepository.schedule_user_leaderboards_update")
    @patch(
        "leaderboard.utils.get_leaderboards_initialization_status",
        return_value=LeaderboardsInitializationStatus.COMPLETED,
    )
    def test_logs_and_swallows_when_both_paths_fail(
        self,
        mock_status: MagicMock,
        mock_schedule: MagicMock,
        mock_task: MagicMock,
    ) -> None:
        mock_task.delay.side_effect = ConnectionError("Redis broker down")
        mock_schedule.side_effect = ConnectionError("Redis completely down")

        # Should not raise
        _safe_enqueue_leaderboard_update("user-1")


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


class TestLeaderboardsUserDeletion:
    @pytest.mark.django_db(transaction=True)
    @patch("leaderboard.tasks.task_remove_user_from_leaderboards")
    def test_removal_task_is_scheduled_if_user_deletion_transaction_is_committed(
        self,
        task_remove_user_from_leaderboards_mock: MagicMock,
        gamma_user_factory: Type[GammaUserFactory],
    ) -> None:
        """
        Test that deleting a GammaUser schedules the removal task after transaction commit.
        """
        user_uid = "test_user"
        signup_source = "test_source"
        gamma_user = gamma_user_factory(user_uid=user_uid, signup_source=signup_source)

        with transaction.atomic():
            gamma_user.delete()

        task_remove_user_from_leaderboards_mock.delay.assert_called_once_with(
            user_uid, signup_source, []
        )

    @pytest.mark.django_db(transaction=True)
    @patch("leaderboard.tasks.task_remove_user_from_leaderboards")
    def test_removal_task_is_not_scheduled_if_user_deletion_transaction_is_not_committed(
        self,
        task_remove_user_from_leaderboards_mock: MagicMock,
        gamma_user_factory: Type[GammaUserFactory],
    ) -> None:
        """
        Test that deleting a GammaUser does not schedule the removal task before transaction commit.
        """
        gamma_user = gamma_user_factory(user_uid="test_user")

        with transaction.atomic():
            gamma_user.delete()

            task_remove_user_from_leaderboards_mock.delay.assert_not_called()

    @pytest.mark.django_db(transaction=True)
    @patch("leaderboard.tasks.task_remove_user_from_leaderboards")
    def test_removal_task_includes_course_ids_when_user_has_course_points(
        self,
        task_remove_user_from_leaderboards_mock: MagicMock,
        gamma_user_factory: Type[GammaUserFactory],
        gamma_user_course_points_factory: Type[GammaUserCoursePointsFactory],
    ) -> None:
        """
        Test that deleting a GammaUser with course points includes course IDs in the removal task.
        """
        user_uid = "test_user"
        signup_source = "main"
        gamma_user = gamma_user_factory(user_uid=user_uid, signup_source=signup_source)

        # Create course points for this user
        course_1 = gamma_user_course_points_factory(gamma_user=gamma_user, course_id="course-1")
        course_2 = gamma_user_course_points_factory(gamma_user=gamma_user, course_id="course-2")

        with transaction.atomic():
            gamma_user.delete()

        # Verify the task was called with the correct course IDs
        task_remove_user_from_leaderboards_mock.delay.assert_called_once()
        call_args = task_remove_user_from_leaderboards_mock.delay.call_args[0]

        assert call_args[0] == user_uid
        assert call_args[1] == signup_source
        assert set(call_args[2]) == {"course-1", "course-2"}

    @pytest.mark.django_db(transaction=True)
    @patch("leaderboard.tasks.task_remove_user_from_leaderboards")
    def test_removal_task_is_not_called_on_transaction_rollback(
        self,
        task_remove_user_from_leaderboards_mock: MagicMock,
        gamma_user_factory: Type[GammaUserFactory],
    ) -> None:
        """
        Test that the removal task is not called if the transaction is rolled back.
        """
        gamma_user = gamma_user_factory(user_uid="test_user")

        try:
            with transaction.atomic():
                gamma_user.delete()
                # Force a rollback by raising an exception
                raise Exception("Force rollback")
        except Exception:
            pass

        # Verify the task was not called because the transaction was rolled back
        task_remove_user_from_leaderboards_mock.delay.assert_not_called()

    @pytest.mark.django_db(transaction=True)
    @patch("leaderboard.tasks.task_remove_user_from_leaderboards")
    def test_removal_task_handles_user_without_signup_source(
        self,
        task_remove_user_from_leaderboards_mock: MagicMock,
        gamma_user_factory: Type[GammaUserFactory],
    ) -> None:
        """
        Test that deleting a GammaUser without signup_source still schedules the removal task.
        """
        user_uid = "test_user"
        gamma_user = gamma_user_factory(user_uid=user_uid, signup_source=None)

        with transaction.atomic():
            gamma_user.delete()

        task_remove_user_from_leaderboards_mock.delay.assert_called_once_with(
            user_uid, None, []
        )

from typing import List, Optional

from celery import shared_task

from leaderboard import repository, usecases


@shared_task
def task_initialize_leaderboards(offset: int, batch_size: int) -> None:
    """
    The task that runs leaderboards initialization.
    """
    redis_leaderboard_repository = repository.RedisLeaderboardRepository()
    leaderboard_member_data_repository = repository.ORMLeaderboardMemberDataRepository()

    usecases.InitializeLeaderboardsUseCase(
        redis_leaderboard_repository,
        leaderboard_member_data_repository,
    ).execute(offset, batch_size)


@shared_task
def task_enqueue_leaderboards_user_data_update(user_uid: str) -> None:
    """
    The task that schedules a user to update his leaderboards data.
    """
    leaderboards_pending_update_repository = repository.RedisLeaderboardsPendingUpdateRepository()
    usecases.EnqueueLeaderboardsUpdateUseCase(leaderboards_pending_update_repository).execute(user_uid)


@shared_task
def task_update_leaderboards() -> None:
    """
    The task that runs leaderboards update.
    """
    leaderboard_repository = repository.RedisLeaderboardRepository()
    leaderboard_member_data_repository = repository.ORMLeaderboardMemberDataRepository()
    leaderboards_pending_update_repository = repository.RedisLeaderboardsPendingUpdateRepository()

    usecases.UpdateLeaderboardsUseCase(
        leaderboard_repository,
        leaderboard_member_data_repository,
        leaderboards_pending_update_repository,
    ).execute()


@shared_task
def task_remove_user_from_leaderboards(
    user_uid: str,
    signup_source: Optional[str],
    course_ids: List[str],
) -> None:
    """
    The task that removes user from all their leaderboards.

    This is triggered when a GammaUser is deleted.
    """
    leaderboard_repository = repository.RedisLeaderboardRepository()
    usecases.RemoveUserFromLeaderboardsUseCase(leaderboard_repository).execute(
        user_uid,
        signup_source,
        course_ids,
    )

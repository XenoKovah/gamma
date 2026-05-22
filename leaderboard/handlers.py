import logging
from typing import Type

from django.db import transaction
from django.db.models.signals import pre_delete, pre_save, post_delete
from django.dispatch import receiver

from leaderboard import tasks
from leaderboard.enums import LeaderboardsInitializationStatus
from users.models import GammaUser

logger = logging.getLogger(__name__)


def _safe_enqueue_leaderboard_update(user_uid: str) -> None:
    """
    Dispatch enqueue task with fallback to direct Redis write.
    """
    try:
        tasks.task_enqueue_leaderboards_user_data_update.delay(user_uid)
    except Exception:
        logger.exception("Failed to dispatch leaderboard enqueue task for user %s, using direct fallback", user_uid)
        try:
            from leaderboard.utils import get_leaderboards_initialization_status
            from leaderboard.repository import RedisLeaderboardsPendingUpdateRepository

            if get_leaderboards_initialization_status() == LeaderboardsInitializationStatus.COMPLETED:
                RedisLeaderboardsPendingUpdateRepository().schedule_user_leaderboards_update(user_uid)
        except Exception:
            logger.exception("Fallback enqueue also failed for user %s", user_uid)


@receiver(pre_save, sender=GammaUser)
def enqueue_leaderboards_user_data_update(sender: Type[GammaUser], instance: GammaUser, **kwargs) -> None:
    """
    Add user to the set of users whose leaderboards' data must be recalculated.

    Schedule the user's leaderboards' data update task only if the new Gamma
    user is created or the existed user points count is changed.
    """
    update_fields = kwargs["update_fields"] or ()

    if instance.pk and "points" not in update_fields:
        return

    transaction.on_commit(lambda: _safe_enqueue_leaderboard_update(instance.user_uid))


@receiver(pre_delete, sender=GammaUser)
def cache_user_course_ids_before_deletion(sender: Type[GammaUser], instance: GammaUser, **kwargs) -> None:
    """
    Cache course IDs before cascade delete removes them.

    When a GammaUser is deleted, its related GammaUserCoursePoints are cascade-deleted.
    We need to capture the course IDs before that happens so we can remove the user
    from course leaderboards in the post_delete handler.
    """
    instance._course_ids_for_leaderboard_removal = list(instance.courses_points.values_list("course_id", flat=True))


@receiver(post_delete, sender=GammaUser)
def remove_user_from_leaderboards(sender: Type[GammaUser], instance: GammaUser, **kwargs) -> None:
    """
    Remove deleted user from all leaderboards.

    This ensures Redis leaderboards stay in sync when users are deleted from the admin panel.
    """
    course_ids = getattr(instance, "_course_ids_for_leaderboard_removal", [])

    def _dispatch():
        try:
            tasks.task_remove_user_from_leaderboards.delay(
                instance.user_uid,
                instance.signup_source,
                course_ids,
            )
        except Exception:
            logger.exception(
                "Failed to dispatch leaderboard removal task for user %s",
                instance.user_uid,
            )

    transaction.on_commit(_dispatch)

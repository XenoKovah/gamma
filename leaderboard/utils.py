from django.core.cache import cache

from leaderboard.constants import LEADERBOARDS_INITIALIZATION_BATCHES_LEFT_COUNT_CACHE_KEY


def is_leaderboards_updating_allowed() -> bool:
    """
    Decide whether the leaderboards updating is allowed.

    The updating is allowed if the leaderboards' initialization is finished.
    """
    redis_client = cache.get_client(None)
    leaderboard_initialization_batches_left = redis_client.get(LEADERBOARDS_INITIALIZATION_BATCHES_LEFT_COUNT_CACHE_KEY)

    leaderboards_initialization_started = leaderboard_initialization_batches_left is not None
    leaderboards_initialization_is_in_progress = (
        leaderboards_initialization_started and int(leaderboard_initialization_batches_left) > 0
    )
    return leaderboards_initialization_started and not leaderboards_initialization_is_in_progress

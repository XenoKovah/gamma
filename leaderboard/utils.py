from django.core.cache import cache
from redis import Redis

from leaderboard.constants import LEADERBOARDS_INITIALIZATION_BATCHES_LEFT_COUNT_CACHE_KEY
from leaderboard.enums import LeaderboardsInitializationStatus


def get_redis_client() -> Redis:
    """
    Provide the Redis client.
    """
    return cache.get_client(None)


def get_leaderboards_initialization_status() -> LeaderboardsInitializationStatus:
    """
    Provide the status of the leaderboards initialization process.
    """
    redis_client = get_redis_client()
    leaderboard_initialization_batches_left = redis_client.get(LEADERBOARDS_INITIALIZATION_BATCHES_LEFT_COUNT_CACHE_KEY)

    if leaderboard_initialization_batches_left is None:
        return LeaderboardsInitializationStatus.NOT_STARTED

    leaderboard_initialization_batches_left = int(leaderboard_initialization_batches_left)

    if leaderboard_initialization_batches_left > 0:
        return LeaderboardsInitializationStatus.IN_PROGRESS

    return LeaderboardsInitializationStatus.COMPLETED

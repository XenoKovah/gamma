from enum import Enum, auto


class LeaderboardsInitializationStatus(Enum):
    """
    Enumerate leaderboards initialization statuses.
    """

    NOT_STARTED = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()

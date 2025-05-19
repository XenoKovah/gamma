from typing import Dict, TypedDict


class GeneralProgress(TypedDict):
    """
    Represent general progress tracking for an event.
    """

    goal: int
    last: str
    count: int


class AchievedConditionMixin(TypedDict):
    """
    Represent a condition indicating whether an achievement rule has been obtained.
    """

    is_achieved: bool


class AchievementObtainedProgress(TypedDict):
    """
    Represent the progress of an obtained achievement.
    """

    dependent_content_type: str
    dependent_object_id: int


class CommonEventDependencies(AchievedConditionMixin):
    """
    Represent dependencies for common events.
    """

    events: Dict[str, GeneralProgress]


class PointsDistributionEventDependencies(TypedDict, AchievedConditionMixin):
    """
    Represent dependencies for points distribution events.
    """

    points: Dict[str, GeneralProgress]


class AchievementObtainedDependencies(TypedDict, AchievedConditionMixin):
    """
    Represent dependencies for obtained achievement events.
    """

    achievements: Dict[str, AchievementObtainedProgress]

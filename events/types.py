from typing import Dict, TypedDict, Union


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


class EventDependencies(AchievedConditionMixin):
    """
    Represent dependencies for common events.
    """

    events: Dict[str, Union[GeneralProgress, AchievementObtainedProgress]]

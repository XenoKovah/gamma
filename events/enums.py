from enum import Enum
from typing import List


class RggInternalEventTypes(Enum):
    """
    Enumeration of internal event types for the RGG system.
    """

    RGG_POINTS_DISTRIBUTION = ('rgg_points_distribution', 'Points Distribution')
    RGG_ACHIEVEMENT_OBTAINED = ('rgg_achievement_obtained', 'Achievement Obtained')

    def __init__(self, value: str, title: str):
        self._value_ = value
        self._title = title

    @classmethod
    def get_all(cls) -> List[str]:
        """
        Retrieve all internal event type values.
        """
        return [c.value for c in cls]

    @property
    def title(self) -> str:
        return self._title

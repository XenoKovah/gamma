from enum import Enum
from typing import List, Optional


class AchievementTypes(Enum):
    """
    Enumeration of different achievement types.
    """

    BADGE = 'badge'
    AVATAR = 'avatar'

    @classmethod
    def get_all(cls) -> List[str]:
        """
        Retrieve all achievement type values.
        """
        return [c.value for c in cls]

    @classmethod
    def from_value(cls, value: Optional[str] = None) -> Optional['AchievementTypes']:
        """
        Return the AchievementTypes member corresponding to the given value.
        """
        if not value:
            return None

        try:
            return cls(value)
        except ValueError as exc:
            raise ValueError(f'Invalid AchievementTypes value: {value}') from exc

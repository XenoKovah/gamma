from enum import Enum
from typing import List


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

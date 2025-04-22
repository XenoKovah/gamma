from typing import Literal

from achievements.enums import AchievementTypes

AchievementTypeLiteral = Literal[tuple(AchievementTypes.get_all())]

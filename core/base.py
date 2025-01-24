from abc import ABC, abstractmethod

from events.models import Event
from rules.models import Rule


class AchievementBackend(ABC):
    """
    Represents abstract class for achievement backends.
    """
    NAME = None

    @abstractmethod
    def create_draft_achievement(self, rule: Rule, event: Event) -> None:
        """
        Creates a draft achievement for a given rule and event based on current backend.

        Iterates over chosen backend by affected rules and creates achievement with related rules.
        """
        pass

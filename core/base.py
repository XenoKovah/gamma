from abc import ABC, abstractmethod

from events.models import Event
from rules.models import Rule
from users.models import GammaUser


class AchievementBackend(ABC):
    """
    Represents abstract class for achievement backends.
    """
    NAME = None

    @abstractmethod
    def process_achievement(self, rule: Rule, event: Event, user: GammaUser) -> None:
        """
        Check whether create or update draft achievements for a given rule and event based on current backend.

        Iterates over chosen backend by affected rules and creates achievement with related rules.
        """
        pass


class UseCase(ABC):
    """
    Represent the abstract Use Case.
    """

    @abstractmethod
    def execute(self, *args, **kwargs):
        """
        Execute Use Case business logic.
        """

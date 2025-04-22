import logging

from django.db import transaction

from achievements.usecases import CreateUserAchievementBasedOnEventUseCase, UpdateUserAchievementBasedOnEventUseCase
from badges.models import Badge
from core.base import AchievementBackend
from events.models import Event
from rules.models import Rule
from users.models import GammaUser

logger = logging.getLogger(__name__)


class BadgeBackend(AchievementBackend):
    """
    The class is an implementation of the AchievementBackend for managing badge-related achievements.

    Define methods for creating draft achievements tied to specific badges based on rules and events.
    """

    NAME = 'badge'

    def process_achievement(self, rule: Rule, event: Event, user: GammaUser):
        badges = Badge.objects.filter(rules=rule).prefetch_related('rules')

        if not badges.exists():
            return

        for badge in badges:
            action = self.update_achievement if badge.has_achievement(user) else self.create_achievement
            action(badge, user, event)

    @transaction.atomic
    def create_achievement(self, badge: Badge, user: GammaUser, event: Event) -> None:
        """
        Create a draft achievement for a specific badge and assigns it to a user.
        """
        CreateUserAchievementBasedOnEventUseCase().execute(badge, user, event)

    @transaction.atomic
    def update_achievement(self, badge: Badge, user: GammaUser, event: Event) -> None:
        """
        Update a draft achievement for a specific badge and assigns it to a user.
        """
        UpdateUserAchievementBasedOnEventUseCase().execute(badge, user, event)

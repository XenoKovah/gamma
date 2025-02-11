import logging

from django.contrib.auth import get_user_model
from django.db import transaction

from achievements.models import Achievement
from badges.models import Badge
from core.base import AchievementBackend
from events.models import Event
from rules.models import Rule
from users.models import GammaUser

User = get_user_model()
logger = logging.getLogger(__name__)


class BadgeBackend(AchievementBackend):
    """
    The class is an implementation of the AchievementBackend for managing badge-related achievements.

    It defines methods for creating draft achievements tied to specific badges based on rules and events.
    """

    NAME = 'badge'

    def process_achievement(self, rule: Rule, event: Event, user: GammaUser, is_achievement_exists: bool):
        badges = Badge.objects.filter(rules=rule).prefetch_related('rules')

        if not badges.exists():
            return

        action = self.update_achievement if is_achievement_exists else self.create_achievement
        for badge in badges:
            action(badge, user, event)

    @transaction.atomic
    def create_achievement(self, badge, user, event) -> None:
        """
        Create a draft achievement for a specific badge and assigns it to a user.
        """
        achievement = Achievement.objects.create_achievement(user, event, badge)
        logger.info('Created draft: <%s>', achievement)

    @transaction.atomic
    def update_achievement(self, badge, user, event) -> None:
        """
        Update a draft achievement for a specific badge and assigns it to a user.
        """
        achievement = Achievement.objects.update_achievement(user, event, badge)
        logger.info('Updated draft: <%s>', achievement)

import logging

from django.contrib.auth import get_user_model
from django.db import transaction

from achievements.models import Achievement
from avatars.models import Avatar
from core.base import AchievementBackend
from events.models import Event
from rules.models import Rule
from users.models import GammaUser


User = get_user_model()
logger = logging.getLogger(__name__)


class AvatarBackend(AchievementBackend):
    """
    The class is an implementation of the AchievementBackend for managing avatar-related achievements.

    It defines methods for creating draft achievements tied to specific avatars based on rules and events.
    """

    NAME = 'avatar'

    def process_achievement(self, rule: Rule, event: Event, user: GammaUser, is_achievement_exists: bool):
        avatars = Avatar.objects.filter(rules=rule).prefetch_related('rules')

        if not avatars.exists():
            return

        action = self.update_achievement if is_achievement_exists else self.create_achievement
        for avatar in avatars:
            action(avatar, user, event)

    @transaction.atomic
    def create_achievement(self, avatar, user, event) -> None:
        """
        Create a draft achievement for a specific badge and assigns it to a user.
        """
        achievement = Achievement.objects.create_achievement(user, event, avatar)
        logger.info('Created draft: <%s>', achievement)

    @transaction.atomic
    def update_achievement(self, avatar, user, event) -> None:
        """
        Update a draft achievement for a specific badge and assigns it to a user.
        """
        achievement = Achievement.objects.update_achievement(user, event, avatar)
        logger.info('Updated draft: <%s>', achievement)

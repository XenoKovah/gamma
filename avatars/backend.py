import logging

from django.contrib.auth import get_user_model
from django.db import transaction

from achievements.usecases import CreateUserAchievementBasedOnEventUseCase, UpdateUserAchievementBasedOnEventUseCase
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

    Define methods for creating draft achievements tied to specific avatars based on rules and events.
    """

    def process_achievement(self, rule: Rule, event: Event, user: GammaUser):
        avatars = Avatar.objects.filter(rules=rule).prefetch_related('rules')

        if not avatars.exists():
            return

        for avatar in avatars:
            action = self.update_achievement if avatar.has_achievement(user) else self.create_achievement
            action(avatar, user, event)

    @transaction.atomic
    def create_achievement(self, avatar: Avatar, user: GammaUser, event: Event) -> None:
        """
        Create a draft achievement for a specific badge and assigns it to a user.
        """
        CreateUserAchievementBasedOnEventUseCase().execute(avatar, user, event)

    @transaction.atomic
    def update_achievement(self, avatar: Avatar, user: GammaUser, event: Event) -> None:
        """
        Update a draft achievement for a specific badge and assigns it to a user.
        """
        UpdateUserAchievementBasedOnEventUseCase().execute(avatar, user, event)

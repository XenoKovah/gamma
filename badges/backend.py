from django.contrib.auth import get_user_model
from django.db import transaction

from achievements.models import Achievement
from badges.models import Badge
from core.base import AchievementBackend


User = get_user_model()


class BadgeBackend(AchievementBackend):
    """
    The class is an implementation of the AchievementBackend for managing badge-related achievements.

    It defines methods for creating draft achievements tied to specific badges based on rules and events.
    """

    NAME = 'badge'

    def create_draft_achievement(self, rule, event):
        badges = Badge.objects.filter(rules=rule).prefetch_related('rules')
        user = User.objects.get(username=event.username)

        for badge in badges:
            self.draft_achievement_from_badge(badge, user, event)

    @transaction.atomic
    def draft_achievement_from_badge(self, badge, user, event) -> None:
        """
        Creates a draft achievement for a specific badge and assigns it to a user.
        """
        Achievement.objects.create_draft_achievement(user, event, badge)

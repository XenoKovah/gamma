"""
Avatar progress service logic.
"""

from __future__ import annotations

import logging
from dataclasses import asdict
from typing import Any, Dict, Optional, TYPE_CHECKING

from django.db.models import Count, F, Q

from achievements.models import AchievementRule
from achievements.services.base import BaseProgressService
from achievements.data import AvatarProgressResult
from avatars.models import UserAvatarConfig
from events.enums import RggInternalEventTypes

if TYPE_CHECKING:
    from avatars.models import Avatar


logger = logging.getLogger(__name__)


class AvatarProgressService(BaseProgressService):
    """
    Avatar-specific progress service.
    """

    def __init__(self, username: str, config: Optional[UserAvatarConfig] = None) -> None:
        if config is not None and isinstance(config, UserAvatarConfig):
            self.config = config
        else:
            self.config = (
                UserAvatarConfig.objects.select_related('user', 'avatar_set')
                .prefetch_related('avatar_set__avatars__rules')
                .get(user__user_uid=username)
            )

        self.user = getattr(self.config, 'user', None)
        self.avatar_set = getattr(self.config, 'avatar_set', None)

    def calculate_progress(self) -> Dict:
        """
        Calculate the current user's progress towards unlocking their avatar.
        """
        current_avatar = self.resolve_current()
        next_avatar = self.resolve_next(last_achieved=current_avatar)

        current_points = getattr(self.user, 'points', 0)
        required_points_for_avatar = self._get_required_points_for_avatar(next_avatar)

        last_avatar = self.resolve_last()
        max_required_points = self._get_required_points_for_avatar(last_avatar)

        return asdict(
            AvatarProgressResult(
                current_points=current_points,
                required_points=required_points_for_avatar,
                max_required_points=max_required_points,
                current_avatar=self._serialize_target(current_avatar),
                next_avatar=self._serialize_target(next_avatar),
            )
        )

    def resolve_current(self) -> Optional[Avatar]:
        """
        Return the user's last achieved avatar.
        """
        if not (getattr(self.avatar_set, 'id', None) and getattr(self.user, 'id', None)):
            return None

        avatars_qs = (
            self.avatar_set.avatars.annotate(
                total_rules=Count('rules', distinct=True),
                completed_rules=Count(
                    'rules',
                    filter=Q(
                        rules__rule_achievements__achievement__user=self.user,
                        rules__rule_achievements__status=AchievementRule.Statuses.COMPLETED,
                        rules__rule_achievements__achievement__object_id__in=self.avatar_set.avatars.values_list(
                            'id', flat=True
                        ),
                    ),
                    distinct=True,
                ),
            )
            .filter(total_rules=F('completed_rules'))
            .order_by('-stage')
        )
        return avatars_qs.first()

    def resolve_next(self, last_achieved: Optional[Avatar] = None) -> Optional[Avatar]:
        """
        Return the next avatar that the user should unlock.
        """
        if not getattr(self.avatar_set, 'id', None):
            return None

        last_avatar = last_achieved or self.resolve_current()
        avatars = self.avatar_set.avatars.order_by('stage')
        if not last_avatar:
            return avatars.first()

        return avatars.filter(stage__gt=last_avatar.stage).first()

    def resolve_last(self) -> Optional[Avatar]:
        """
        Return the last avatar in the avatar set (the one with the highest stage).
        """
        if not self.avatar_set:
            return None

        return (
            self.avatar_set.avatars
            .exclude(stage__isnull=True)
            .order_by('-stage')
            .first()
        )

    @staticmethod
    def build_empty_progress() -> AvatarProgressResult:
        """
        Return default empty progress for users without avatars configured.
        """
        return AvatarProgressResult(
            current_points=0,
            required_points=0,
            max_required_points=0,
            current_avatar=None,
            next_avatar=None,
        )

    @staticmethod
    def _serialize_target(target: Any) -> Optional[Dict]:
        """
        Serialize avatar target object to dict.
        """
        if target is None:
            return None

        return {
            'id': getattr(target, 'id', None),
            'title': getattr(target, 'title', None),
            'stage': getattr(target, 'stage', None),
            'image': getattr(getattr(target, 'image', None), 'url', None),
            'description': getattr(target, 'description', None),
        }

    @staticmethod
    def _get_required_points_for_avatar(avatar: Optional[Avatar]) -> int:
        """
        Return required points from avatar's rules where action references point progression.
        """
        if not avatar:
            return 0

        total_points = 0
        for rule in avatar.rules.all():
            action = getattr(rule, 'action', {}) or {}
            points_mark = action.get(RggInternalEventTypes.RGG_POINTS_DISTRIBUTION.value)
            if isinstance(points_mark, dict) and 'points' in points_mark:
                try:
                    total_points += int(points_mark['points'])
                except (TypeError, ValueError):
                    continue
        return total_points


def get_avatar_progress_service(
    username: Optional[str] = None,
    config: Optional[UserAvatarConfig] = None,
) -> AvatarProgressService:
    """
    Factory method to get AvatarProgressService instance.
    """
    return AvatarProgressService(username=username, config=config)

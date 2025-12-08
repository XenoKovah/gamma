"""
Events service logic.
"""

from typing import Optional, Set, Tuple, Union

from django.db.models import QuerySet

from achievements.enums import AchievementTypes
from events.enums import EdxCommonEventTypes, RggInternalEventTypes
from events.models import EventConfiguration


class EventConfigurationService:
    """
    Provides available EventConfiguration entries for a given AchievementType.
    """

    def __init__(self, achievement_type: Optional[AchievementTypes] = None):
        self.achievement_type: Optional[AchievementTypes] = achievement_type

    # Common event configuration that should never be available for any achievement.
    COMMON_EXCLUDED: Set[str] = {RggInternalEventTypes.RGG_ACHIEVEMENT_OBTAINED.value}

    # Per-type exclusion sets.
    BADGE_EXCLUDED: Set[str] = set()
    AVATAR_EXCLUDED: Set[str] = set()

    TYPE_EXCLUDES = {
        AchievementTypes.BADGE: BADGE_EXCLUDED,
        AchievementTypes.AVATAR: AVATAR_EXCLUDED,
    }

    # Per-type allow lists. When defined (non-empty), they restrict the results.
    BADGE_ALLOWED: Set[str] = set()
    AVATAR_ALLOWED: Set[str] = {RggInternalEventTypes.RGG_POINTS_DISTRIBUTION.value}

    TYPE_ALLOWED = {
        AchievementTypes.BADGE: BADGE_ALLOWED,
        AchievementTypes.AVATAR: AVATAR_ALLOWED,
    }

    def get_excluded(self) -> Tuple[str, ...]:
        """
        Return combined excluded values (common + type-specific).
        """
        type_excludes = self.TYPE_EXCLUDES.get(self.achievement_type, set())
        combined = self.COMMON_EXCLUDED | type_excludes
        return tuple(combined)

    def get_allowed(self) -> Optional[Tuple[str, ...]]:
        """
        Return allowed tuple or None if not defined/empty.

        None means "no allow-list defined; use excludes only".
        """
        allowed_set = self.TYPE_ALLOWED.get(self.achievement_type, set())
        if not allowed_set:
            return None

        return tuple(allowed_set)

    def get_available(self) -> QuerySet[EventConfiguration]:
        """
        Return available EventConfiguration QuerySet for the given achievement_type.
        - Build the excluded set (common + type-specific).
        - If an allowed list exists (non-empty), compute allowed_set - excluded_set.
        - If that result is empty, return an empty queryset.
        - Otherwise, exclude the excluded_set from all EventConfiguration objects.
        """
        excluded_set = self.COMMON_EXCLUDED | self.TYPE_EXCLUDES.get(self.achievement_type, set())
        allowed_set = self.TYPE_ALLOWED.get(self.achievement_type, None)

        if allowed_set:
            effective_allowed = allowed_set - excluded_set
            if not effective_allowed:
                return EventConfiguration.objects.none()
            return EventConfiguration.objects.filter(event_type__name__in=effective_allowed)

        if excluded_set:
            return EventConfiguration.objects.exclude(event_type__name__in=excluded_set)

        return EventConfiguration.objects.all()

    def is_allowed(self, event_configuration_name: Union[RggInternalEventTypes, EdxCommonEventTypes]) -> bool:
        """
        Check whether the event type name is allowed for the current achievement type.
        """
        if not isinstance(event_configuration_name, (RggInternalEventTypes, EdxCommonEventTypes)):
            return

        value = event_configuration_name.value
        allowed = self.get_allowed()
        excluded = self.get_excluded()

        if allowed is not None:
            return value in allowed and value not in excluded

        return value not in excluded

def get_event_configuration_service(achievement_type: Optional[AchievementTypes] = None) -> EventConfigurationService:
    """
    Factory method to get EventConfigurationService instance.
    """
    return EventConfigurationService(achievement_type=achievement_type)

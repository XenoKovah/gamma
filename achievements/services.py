import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from events.models import EventConfiguration
from rules.models import Rule

logger = logging.getLogger(__name__)


class RuleDependencyService:
    """
    Class-based service to update dependencies for achievement rule.
    """

    events_key_name = 'events'
    achievements_key_name = 'achievements'

    def __init__(self, rule: Rule, event_created_at: datetime, initial_dependencies: dict = None):
        self.rule = rule
        self.event_created_at = event_created_at
        self.dependencies = {
            k: v.copy() for k, v in (initial_dependencies or {}).items() if v
        }
        self._handler_map = {
            **{event: self._handle_event for event in self._get_event_types()},
            **{achievement: self._handle_dependent_achievement for achievement in self._get_achievement_types()},
        }

    def create_or_update(self, actions: Dict[str, int]) -> dict:
        """
        Update dependencies dynamically by dispatching to the appropriate handlers.
        """
        if not isinstance(actions, dict):
            logger.error('Invalid actions format: Expected a dictionary but got %s', type(actions))
            return self.dependencies

        for action_type, value in actions.items():
            if not isinstance(action_type, str) or not isinstance(value, int):
                logger.warning('Skipping invalid action entry: [%s] = %s', action_type, value)
                continue

            handler = self._handler_map.get(action_type)
            if handler:
                if handler == self._handle_event:
                    handler(action_type, value)
                else:
                    handler(value)
            else:
                logger.warning('Unrecognized action: %s', action_type)

        return {k: v for k, v in self.dependencies.items() if v}

    def _handle_event(self, action_type: str, value: int):
        """
        Handle external event-based dependencies (event key) with frequency check.

        If a frequency rule exists and isn't met, progress is reset to 1.
        Otherwise, it increments the event count.
        """
        events = self.dependencies.setdefault(self.events_key_name, {})
        event_progress = events.get(action_type, {})

        if not self._check_frequency_fit(self.rule.filters, event_progress):
            events[action_type] = {
                'count': 1,
                'goal': value,
                'last': self.event_created_at.isoformat(),
            }
        else:
            events[action_type] = {
                'count': event_progress.get('count', 0) + 1,
                'goal': value,
                'last': self.event_created_at.isoformat(),
            }

    def _handle_dependent_achievement(self, value: int):
        """
        Handle internal dependencies (achievements key).

        To handle the dependent badge event configuration for an event, the processing should ensure:
        - `is_depends_on_achievement` is set to `True`.
        - The appropriate content type is selected, e.g. Badge
        """
        achievements = self.dependencies.setdefault(self.achievements_key_name, [])

        existing_achievements = {(achieve['content_type'], achieve['id']) for achieve in achievements}
        content_type = self.rule.achievement_content_type

        if not content_type:
            logger.error('Incorrect %s setup: Skipping invalid.', self.rule.event_configuration)
            return

        if (content_type.name, value) not in existing_achievements:
            achievements.append(
                {'content_type_id': content_type.id, 'content_type': content_type.name, 'id': value}
            )

    def _check_frequency_fit(self, filters: Optional[Dict[str, Any]], progress: Dict[str, Any]) -> bool:
        """
        Check if frequency rule is performed for the event.

        Frequency is count of days between same type events,
        i.e. Frequency 2 means that if some type of event for badge is not
        performed during 2 days, badge progress for the event should be reset
        to 1 when new event of this type is received.
        Other events from rules won't be affected.
        """
        if not filters:
            return True

        if frequency_filter := filters.get('frequency'):

            try:
                delta = timedelta(int(frequency_filter))
            except (ValueError, TypeError):
                logger.warning('Invalid frequency value: %s. Skipping frequency check.', frequency_filter)
                return True

            last = progress.get('last')
            if not last:
                logger.warning('Missing last event timestamp for action type.')
                return True

            try:
                last_datetime = datetime.fromisoformat(last)
            except ValueError:
                logger.warning('Invalid datetime format in progress: %s. Skipping frequency check.', last)
                return True

            time_diff = self.event_created_at - last_datetime
            if time_diff > delta:
                return False

        return True

    def _get_achievement_types(self) -> List[str]:
        """
        Return available achievement triggered event names.
        """
        return EventConfiguration.available_achievement_based_names()

    def _get_event_types(self) -> List[str]:
        """
        Return available event names.
        """
        return EventConfiguration.available_event_based_names()

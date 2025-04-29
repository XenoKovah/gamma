import copy
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from functools import lru_cache
from typing import Any, Dict, Optional, Type, Union

from schematics.exceptions import DataError
from schematics.models import Model

from achievements.exceptions import AchievementRuleProcessingException
from achievements.models import Achievement, AchievementRule
from events import schemas, types
from events.dataclasses import EventProgress
from events.enums import RggInternalEventTypes
from events.models import Event, EventConfiguration
from users.models import GammaUser

logger = logging.getLogger(__name__)


class EventProcessorFactory:
    """
    Encapsulate the logic for using the correct processor instance depending on the type of event.
    """

    @classmethod
    @lru_cache(maxsize=32)
    def get_processor(cls, event_name: str):
        """
        Select the appropriate processor based on event name.
        """
        if event_name in TRACKING_EVENT_PROCESSORS_MAP:
            return TRACKING_EVENT_PROCESSORS_MAP[event_name]()

        if event_name in EventConfiguration.available_common_event_names():
            return CommonEventProcessor()

        raise ValueError(f'Unknown event: {event_name}.')


class BaseEventProcessor(ABC):
    """
    Abstract class for event processing strategies.
    """

    DEPENDENCY_KEY_NAME: Optional[str] = None
    ACTION_SCHEMA: Optional[Type[Model]] = None

    @abstractmethod
    def _process(
        self,
        progress: EventProgress,
        achievement_rule: Optional[AchievementRule] = None,
        user: Optional[GammaUser] = None,
        event: Optional[Event] = None,
    ) -> Union[types.CommonEventDependencies]:
        """
        Process an event and update dependencies accordingly for achievement rule.

        It can be customized for a specific event.
        """
        pass

    def can_process(self, action: dict) -> bool:
        """
        Determine whether the current processor can handle the given event based on provided action data.
        """
        try:
            self.ACTION_SCHEMA(action).validate()
        except TypeError as exc:
            logger.warning('Invalid value for action %s with exception: %s.', action, exc)
            return False
        except DataError as exc:
            logger.warning(
                'Invalid action %r format for schema %r with exception: %s.',
                action,
                self.ACTION_SCHEMA.__name__,
                exc
            )
            return False
        return True

    def process(
        self,
        achievement_rule: AchievementRule,
        user: GammaUser,
        event: Event
    ) -> types.CommonEventDependencies:
        """
        Process an event and calculates dependencies for the given achievement rule.
        """
        logger.info(
            'Start event %r processing for (Achievement Rule: %s, ID: %d) dependency calculation.',
            event.event_name,
            achievement_rule,
            achievement_rule.id,
        )

        progress = self._initialize_progress(achievement_rule, event)
        if not self.can_process(progress.action):
            message = f'Skipping event {event.event_name!r}.'
            logger.warning('%s Achievement dependencies remain unchanged: %s', message, achievement_rule.dependencies)
            raise AchievementRuleProcessingException

        return self._process(progress, achievement_rule, user, event)

    def _initialize_progress(self, achievement_rule: AchievementRule, event: Event):
        """
        Initialize and return the necessary data for event processing needed for achievement dependency.
        """
        dependencies = copy.deepcopy(achievement_rule.dependencies or {})
        current_dependency = dependencies.setdefault(self.DEPENDENCY_KEY_NAME, {})
        progress_by_event = current_dependency.get(event.event_name, {})
        event_name = event.event_name
        action = achievement_rule.rule.action.get(event_name)

        return EventProgress(current_dependency, progress_by_event, event_name, action)


class CommonEventProcessor(BaseEventProcessor):
    """
    Processor for handling common event from gamification-bridge.

    This processor updates the progress of an achievement rule based on event occurrences.
    Validate the event against predefined action schemas and checks whether the achievement criteria are met.
    By inheriting a class it is possible to change the behavior for event processing.
    """

    DEPENDENCY_KEY_NAME = 'events'
    ACTION_SCHEMA = schemas.CountActionSchema

    def _process(
        self,
        progress: EventProgress,
        achievement_rule: AchievementRule,
        user: GammaUser,
        event: Event,
    ) -> types.CommonEventDependencies:
        """
        Process an event and return updated dependencies.
        """
        passed_frequency_filter = self._check_frequency_fit(achievement_rule.rule.filters, progress.current)
        event_count = progress.by_event.get('count', 0) + 1 if passed_frequency_filter else 1
        raw_progress_count = progress.action.get('count')

        try:
            progress_count = int(raw_progress_count)
        except (TypeError, ValueError):
            logger.warning(
                'The progress count of %s rule cannot be processed: %s',
                achievement_rule,
                raw_progress_count
            )
            raise AchievementRuleProcessingException

        is_achieved = event_count >= progress_count
        updated_progress = types.GeneralProgress(
            goal=progress.action['count'],
            last_updated=event.created_at.isoformat(),
            count=event_count,
        )

        return types.CommonEventDependencies(events={progress.event_name: updated_progress}, is_achieved=is_achieved)

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


class RggAchievementObtainedProcessor(BaseEventProcessor):
    """
    Processor for handling achievement obtained events in the RGG system.
    """

    DEPENDENCY_KEY_NAME = 'achievements'
    ACTION_SCHEMA = schemas.RggAchievementObtainedSchema

    def _process(
        self,
        progress: EventProgress,
        achievement_rule: AchievementRule,
        user: GammaUser,
        event: Event,
    ) -> types.AchievementObtainedDependencies:
        """
        Process the event and updates the dependencies to achievements obtaining.
        """
        is_achieved = Achievement.objects.filter(user=user, object_id=progress.action['dependent_object_id']).exists()
        updated_progress = types.AchievementObtainedProgress(**progress.action)

        return types.AchievementObtainedDependencies(
            achievements={progress.event_name: updated_progress},
            is_achieved=is_achieved
        )


class RggPointsDistributionProcessor(BaseEventProcessor):
    """
    Processor for handling points distribution events in the RGG system.
    """

    DEPENDENCY_KEY_NAME = 'points'
    ACTION_SCHEMA = schemas.RggPointDistributionSchema

    def _process(
        self,
        progress: EventProgress,
        achievement_rule: AchievementRule,
        user: GammaUser,
        event: Event
    ) -> types.PointsDistributionEventDependencies:
        """
        Process the event and updates the dependencies with points distribution.
        """
        points = user.points
        raw_progress_points = progress.action.get('points')

        try:
            progress_points = int(raw_progress_points)
        except (TypeError, ValueError):
            logger.warning(
                'The progress points of %s rule cannot be processed: %s',
                achievement_rule,
                raw_progress_points
            )
            raise AchievementRuleProcessingException

        is_achieved = points >= progress_points
        updated_progress = types.GeneralProgress(
            goal=progress.action['points'],
            last_updated=event.created_at.isoformat(),
            count=points,
        )

        return types.PointsDistributionEventDependencies(
            points={progress.event_name: updated_progress},
            is_achieved=is_achieved
        )


TRACKING_EVENT_PROCESSORS_MAP = {
    RggInternalEventTypes.RGG_ACHIEVEMENT_OBTAINED.value: RggAchievementObtainedProcessor,
    RggInternalEventTypes.RGG_POINTS_DISTRIBUTION.value: RggPointsDistributionProcessor,
}

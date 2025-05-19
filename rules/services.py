import logging
from datetime import datetime
from typing import Sequence

from django.utils.timezone import make_aware, utc

from events.models import Event
from rules.models import Rule

from .constants import DATETIME_FORMAT

logger = logging.getLogger('rules.filters')


class RulesFilterService:
    """
    A class to filter rules based on whether they meet the event's filter requirements.
    """

    def __init__(self, event: Event):
        self.event = event

    def filter_rules(self, rules: Sequence[Rule]) -> Sequence[Rule]:
        """
        Filter out the rules that do not meet the event.

        The type of event must be relevant, i.e., the actions of the rules must refer to the corresponding event.
        """
        return [
            rule for rule in rules
            if rule.is_event_type_relevant and self.does_event_pass_filters(rule)
        ]

    def does_event_pass_filters(self, rule: Rule) -> bool:
        """
        Check if the event satisfies the filters in the rule.
        """
        if not rule.filters:
            return True

        filter_methods = [
            self._passes_interval_filter,
            self._passes_org_filter,
            self._passes_course_filter,
        ]

        return all(filter_method(rule) for filter_method in filter_methods)

    def _passes_interval_filter(self, rule: Rule) -> bool:
        """
        Check if the rule passes the interval filter.
        """
        interval = rule.filters.get('interval')
        if not interval:
            return True

        try:
            start_date = self.parse_and_make_aware(interval.get('start'))
            end_date = self.parse_and_make_aware(interval.get('end'))
        except ValueError as err:
            logger.warning('Invalid datetime format: "%s"', err)
            return False

        return not (start_date and end_date and not (start_date <= self.event.created_at <= end_date))

    def _passes_org_filter(self, rule: Rule) -> bool:
        """
        Check if the rule passes the organization filter.
        """
        org = rule.filters.get('org')
        return org is None or self.event.org == org

    def _passes_course_filter(self, rule: Rule) -> bool:
        """
        Check if the rule passes the course filter.
        """
        course = rule.filters.get('course')
        return course is None or self.event.course_id == course

    @staticmethod
    def parse_and_make_aware(date_str: str) -> datetime:
        """
        Parse a string to a timezone-aware datetime.
        """
        if not date_str:
            return None

        naive_dt = datetime.strptime(date_str, DATETIME_FORMAT)
        return make_aware(naive_dt, utc)

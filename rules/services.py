import logging
from datetime import datetime, timedelta
from typing import List, Optional, Sequence

from django.utils.timezone import make_aware, utc

from events.models import Event
from rules.models import Rule

from .constants import DATETIME_FORMAT, WINDOW_NON_ANCHOR_EVENT_TYPES

logger = logging.getLogger('rules.filters')


class RulesFilterService:
    """
    A class to filter rules based on whether they meet the event's filter requirements.
    """

    def __init__(self, event: Event):
        self.event = event
        # Memo for _window_anchor, keyed by the class's course scope. A certificate is
        # judged against every tier rule of the same class (2/4/12 weeks), which would
        # otherwise repeat one identical history lookup per tier.
        self._anchor_cache = {}

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
            self._passes_completion_window_filter,
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

        ``course`` may be a single course id or a list of course ids. A list is an OR group
        (satisfied by any one of them), used to credit any accepted version of a course.
        """
        course = rule.filters.get('course')
        if not course:
            return True
        if isinstance(course, (list, tuple)):
            return self.event.course_id in course
        return self.event.course_id == course

    def _passes_completion_window_filter(self, rule: Rule) -> bool:
        """
        Check the event lands inside the rule's completion window.

        The window grades how quickly a learner finished a class: it is measured from
        their first real piece of work in it (see ``_window_anchor``) to the event being
        processed — in practice the certificate. ``min_weeks`` is exclusive and
        ``max_weeks`` inclusive, so consecutive bands tile without overlapping and a
        certificate can satisfy at most one tier:

            {'max_weeks': 2}                    ->        elapsed <= 2 weeks   (Gold)
            {'min_weeks': 2, 'max_weeks': 4}    -> 2 weeks < elapsed <= 4 weeks (Silver)
            {'min_weeks': 4, 'max_weeks': 12}   -> 4 weeks < elapsed <= 12 weeks (Bronze)

        A learner slower than the widest band matches no rule and earns nothing, which
        is the intended outcome rather than an error.
        """
        window = rule.filters.get('completion_window')
        if not window:
            return True

        anchor_at = self._window_anchor(rule)
        if anchor_at is None:
            # No recorded work before this event, so the learner's pace is unknown. The
            # window is unverifiable and deliberately fails closed: guessing would hand
            # out a tier nobody measured. Expected for anyone whose activity predates
            # event tracking, or whose history was backfilled after the fact.
            logger.info(
                'Completion window unverifiable for %r in %r: no anchoring activity before the event.',
                self.event.username,
                self.event.course_id,
            )
            return False

        elapsed = self.event.created_at - anchor_at
        min_weeks = window.get('min_weeks')
        max_weeks = window.get('max_weeks')

        if min_weeks is not None and elapsed <= timedelta(weeks=min_weeks):
            return False
        if max_weeks is not None and elapsed > timedelta(weeks=max_weeks):
            return False

        return True

    def _window_anchor(self, rule: Rule) -> Optional[datetime]:
        """
        Return when the learner started this class: their earliest qualifying activity in it.

        Scoped to the rule's ``course`` filter rather than to the event's own course id,
        so a multi-run class (one badge listing every accepted run) is treated as a single
        class — someone who began in the 2021 run and certified in the 2024 one is measured
        from when they actually started, not from when they switched runs.

        Only activity strictly before the event counts, which both keeps the elapsed time
        non-negative and matches the question being asked ("how long did this take?").
        Certificates and enrolments never anchor — see WINDOW_NON_ANCHOR_EVENT_TYPES.
        """
        courses = self._course_scope(rule)
        if not courses:
            return None

        cache_key = tuple(courses)
        if cache_key not in self._anchor_cache:
            self._anchor_cache[cache_key] = (
                Event.objects
                .filter(
                    username=self.event.username,
                    course_id__in=courses,
                    created_at__lt=self.event.created_at,
                )
                .exclude(configuration__event_type__name__in=WINDOW_NON_ANCHOR_EVENT_TYPES)
                .order_by('created_at')
                .values_list('created_at', flat=True)
                .first()
            )

        return self._anchor_cache[cache_key]

    def _course_scope(self, rule: Rule) -> List[str]:
        """
        Return the course ids making up the class this rule is about.

        Falls back to the event's own course when the rule is not course-scoped, so a
        window on an unscoped rule still measures within one course instead of sweeping
        the learner's whole history.
        """
        course = rule.filters.get('course')
        if isinstance(course, (list, tuple)):
            return list(course)
        if course:
            return [course]
        return [self.event.course_id] if self.event.course_id else []

    @staticmethod
    def parse_and_make_aware(date_str: str) -> datetime:
        """
        Parse a string to a timezone-aware datetime.
        """
        if not date_str:
            return None

        naive_dt = datetime.strptime(date_str, DATETIME_FORMAT)
        return make_aware(naive_dt, utc)

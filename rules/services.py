import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Sequence

from django.contrib.contenttypes.models import ContentType
from django.db.models import Min, QuerySet
from django.utils.timezone import make_aware, utc

from achievements.models import Achievement
from badges.models import Badge
from events.models import Event
from rules.models import Rule

from .constants import DATETIME_FORMAT, WINDOW_ANCHOR_EVENT_TYPES

logger = logging.getLogger('rules.filters')


def _parse_filter_datetime(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return make_aware(datetime.strptime(value, DATETIME_FORMAT), utc)
    except (ValueError, TypeError):
        return None


def flatten_blocks(blocks) -> List[str]:
    """
    Every usage key in a ``blocks`` filter: one key, or a list of keys and of equivalent-key groups.
    """
    if isinstance(blocks, str):
        return [blocks]
    return [key for entry in blocks or () for key in ([entry] if isinstance(entry, str) else entry)]


def block_units(blocks) -> Dict[str, int]:
    """
    Map each usage key in a ``blocks`` filter to the unit (entry) it stands for.

    An entry is one unit the rule requires: a usage key, or a group of keys for the same
    unit in several versions of a class, any one of which completes it.
    """
    entries = [blocks] if isinstance(blocks, str) else list(blocks or ())
    return {
        key: index
        for index, entry in enumerate(entries)
        for key in ([entry] if isinstance(entry, str) else entry)
    }


def events_matching_rule(rule: Rule) -> QuerySet:
    """
    Events (across all users) that count toward this rule, applying its filters.
    """
    configuration = rule.event_configuration
    if not configuration:
        return Event.objects.none()

    queryset = Event.objects.filter(configuration__event_type__name=configuration.event_name)
    filters = rule.filters or {}
    if course := filters.get('course'):
        if isinstance(course, (list, tuple)):
            queryset = queryset.filter(course_id__in=course)
        else:
            queryset = queryset.filter(course_id=course)
    if org := filters.get('org'):
        queryset = queryset.filter(org=org)
    if blocks := filters.get('blocks'):
        queryset = queryset.filter(block_id__in=flatten_blocks(blocks))

    interval = filters.get('interval') or {}
    if start := _parse_filter_datetime(interval.get('start')):
        queryset = queryset.filter(created_at__gte=start)
    if end := _parse_filter_datetime(interval.get('end')):
        queryset = queryset.filter(created_at__lte=end)

    return queryset


def is_block_set_rule(rule: Rule) -> bool:
    """
    Whether the rule is about a set of blocks (e.g. every "Mark as complete" unit of a section).
    """
    return bool((rule.filters or {}).get('blocks'))


@dataclass(frozen=True)
class BlockSetProgress:
    """
    A learner's standing on a block-set rule.

    ``count`` is how many of the listed units they have completed (a unit listed in several
    versions of a class counts once); ``achieved_at`` is when the goal-th of them was first
    completed, or None while the goal is unmet.
    """

    count: int
    achieved_at: Optional[datetime]


def block_set_progress(rule: Rule, username: str, goal: Optional[int]) -> BlockSetProgress:
    """
    Measure a learner's progress on a block-set rule from their stored events.

    Counting distinct units in the learner's history, instead of advancing a counter per
    incoming event, keeps the result independent of the order the units were marked in,
    includes units marked before the rule (or the learner's Achievement row) existed, and
    never counts a unit twice however many times, or in how many versions of the class, it
    was marked. A unit is completed when it was first marked in any version. For an "all of
    these units" rule, ``achieved_at`` is the moment the last missing unit was marked,
    whichever unit that was, and it stays correct when history is replayed out of order.
    """
    unit_of = block_units(rule.filters.get('blocks'))
    first_by_unit = {}
    for row in (
        events_matching_rule(rule)
        .filter(username=username, block_id__isnull=False)
        .order_by()
        .values('block_id')
        .annotate(first_completed_at=Min('created_at'))
    ):
        unit = unit_of.get(row['block_id'])
        if unit is not None and (unit not in first_by_unit or row['first_completed_at'] < first_by_unit[unit]):
            first_by_unit[unit] = row['first_completed_at']
    first_completions = sorted(first_by_unit.values())
    achieved = goal is not None and 0 < goal <= len(first_completions)
    return BlockSetProgress(
        count=len(first_completions),
        achieved_at=first_completions[goal - 1] if achieved else None,
    )


class RulesFilterService:
    """
    A class to filter rules based on whether they meet the event's filter requirements.
    """

    def __init__(self, event: Event):
        self.event = event
        # Memos for _window_anchor and _holds_tier_of_class, keyed by the class's course
        # scope. A certificate is judged against every tier rule of the same class
        # (2/4/12 weeks), which would otherwise repeat identical lookups per tier.
        self._anchor_cache = {}
        self._tier_held_cache = {}

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
            self._passes_blocks_filter,
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
        their first "Mark as complete" click in it (see ``_window_anchor``) to the event
        being processed — in practice the certificate. ``min_weeks`` is exclusive and
        ``max_weeks`` inclusive, so consecutive bands tile without overlapping and a
        certificate satisfies exactly one tier:

            {'max_weeks': 2}                    ->        elapsed <= 2 weeks   (Gold)
            {'min_weeks': 2, 'max_weeks': 4}    -> 2 weeks < elapsed <= 4 weeks (Silver)
            {'min_weeks': 4, 'max_weeks': 12}   -> 4 weeks < elapsed <= 12 weeks (Bronze)
            {'min_weeks': 12,                   ->           elapsed > 12 weeks (Plain)
             'match_without_anchor': True}          ... or the pace is unmeasurable

        ``match_without_anchor`` makes an open-ended band double as the catch-all for
        learners whose pace cannot be established at all (no recorded work before the
        event). Without it such a learner matches no band and earns nothing. It belongs
        on exactly one band of a set — setting it on two would award both.

        Two cases skip the timing:

        * A learner who already holds a tier of this class earns no other: each
          certificate lands on exactly one band, but a second certificate for the same
          class (another run, or a re-issue) would otherwise add a second tier.
        * A certificate the bridge flags ``beta_completion`` (allowlisted because the
          learner completed the beta of this class) is graded Gold whatever the clicks
          say. It is treated as an instant finish, which lands on the band containing
          zero (Gold, which has no lower bound) and on no other, so the set still awards
          exactly one tier and no rule data has to change.
        """
        window = rule.filters.get('completion_window')
        if not window:
            return True

        if self._holds_tier_of_class(rule):
            return False

        if self.event.beta_completion:
            return self._elapsed_in_band(window, timedelta(0))

        anchor_at = self._window_anchor(rule)
        if anchor_at is None:
            # Nothing recorded before this event, so the learner's pace is unknown:
            # expected for anyone whose activity predates event tracking or whose
            # history was backfilled after the fact. Only the band explicitly claiming
            # the unmeasurable case takes it; the graded bands decline rather than
            # guess at a pace nobody observed.
            claims_unanchored = bool(window.get('match_without_anchor'))
            logger.info(
                'Completion window unmeasurable for %r in %r (no anchoring activity): %s.',
                self.event.username,
                self.event.course_id,
                'claimed by the catch-all band' if claims_unanchored else 'declined by this band',
            )
            return claims_unanchored

        return self._elapsed_in_band(window, self.event.created_at - anchor_at)

    @staticmethod
    def _elapsed_in_band(window: dict, elapsed: timedelta) -> bool:
        """
        Whether ``elapsed`` falls in the band: ``min_weeks`` exclusive, ``max_weeks`` inclusive.
        """
        min_weeks = window.get('min_weeks')
        max_weeks = window.get('max_weeks')

        if min_weeks is not None and elapsed <= timedelta(weeks=min_weeks):
            return False
        if max_weeks is not None and elapsed > timedelta(weeks=max_weeks):
            return False

        return True

    def _holds_tier_of_class(self, rule: Rule) -> bool:
        """
        Whether the learner already holds a completion tier of this rule's class.

        A class's tiers are the badges whose rules carry a ``completion_window`` over the
        same course scope. The first tier earned stands; moving it (e.g. a beta completer's
        earlier Plain to Gold) is a backfill job, which re-files the grant in place.
        """
        scope = tuple(self._course_scope(rule))
        if scope not in self._tier_held_cache:
            held_badges = Achievement.objects.filter(
                user__user_uid=self.event.username,
                content_type=ContentType.objects.get_for_model(Badge),
                completed_at__isnull=False,
            ).values('object_id')
            held_tier_rules = Rule.objects.filter(
                badge__id__in=held_badges,
                event_configuration_id=rule.event_configuration_id,
            ).only('filters')
            self._tier_held_cache[scope] = any(
                (held.filters or {}).get('completion_window') and tuple(self._course_scope(held)) == scope
                for held in held_tier_rules
            )
        return self._tier_held_cache[scope]

    def _window_anchor(self, rule: Rule) -> Optional[datetime]:
        """
        Return when the learner started this class: their first "Mark as complete" click in it.

        Scoped to the rule's ``course`` filter rather than to the event's own course id,
        so a multi-run class (one badge listing every accepted run) is treated as a single
        class — someone who began in the 2021 run and certified in the 2024 one is measured
        from when they actually started, not from when they switched runs.

        Only clicks strictly before the event count, which both keeps the elapsed time
        non-negative and matches the question being asked ("how long did this take?").
        Only edx_done_toggled anchors — see WINDOW_ANCHOR_EVENT_TYPES; videos, answers,
        bookmarks, forum posts, enrollments and certificates never start the clock. The
        lookup is served by ``event_user_course_time_idx`` (username, course_id, created_at).
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
                    configuration__event_type__name__in=WINDOW_ANCHOR_EVENT_TYPES,
                )
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

    def _passes_blocks_filter(self, rule: Rule) -> bool:
        """
        Check if the rule passes the blocks filter.

        ``blocks`` lists usage keys (or groups of equivalent keys, one unit in several
        versions of a class); the event passes when its block_id is any of them. How far
        it takes the learner is measured by block_set_progress. Events that predate
        block_id (NULL) never match a blocks filter; the done-state backfill repairs
        those rows.
        """
        blocks = rule.filters.get('blocks')
        if not blocks:
            return True
        return self.event.block_id in flatten_blocks(blocks)

    @staticmethod
    def parse_and_make_aware(date_str: str) -> datetime:
        """
        Parse a string to a timezone-aware datetime.
        """
        if not date_str:
            return None

        naive_dt = datetime.strptime(date_str, DATETIME_FORMAT)
        return make_aware(naive_dt, utc)

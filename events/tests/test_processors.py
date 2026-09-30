from datetime import datetime

import pytest
from django.utils.timezone import utc

from events.processors import CommonEventProcessor

pytestmark = pytest.mark.django_db

CERT_EVENT = 'edx_certificate_created'
COURSE_A = 'course-v1:org+A+1'
COURSE_B = 'course-v1:org+B+1'


@pytest.fixture
def cert_configuration(event_configuration_factory):
    return event_configuration_factory(event_type__name=CERT_EVENT)


def _make_cert_rule(rule_factory, configuration, course):
    return rule_factory(
        event_configuration=configuration,
        action={CERT_EVENT: {'count': 1}},
        filters={'course': course},
    )


def test_common_processor_counts_event_only_for_matching_course(
    cert_configuration,
    rule_factory,
    achievement_rule_factory,
    event_factory,
    gamma_user_factory,
):
    """
    A certificate earned in one course must not progress a rule scoped to a different course.

    This guards the multi-course badge use case: a badge that holds one certificate rule per
    required course should only be granted once *all* of those courses have been certified,
    not after the first. Without the per-rule filter check a single certificate would progress
    every same-event-type rule on the badge.
    """
    user = gamma_user_factory()
    rule_b = _make_cert_rule(rule_factory, cert_configuration, COURSE_B)
    achievement_rule_b = achievement_rule_factory(rule=rule_b, dependencies={})

    processor = CommonEventProcessor()

    # Certificate in course A: the rule scoped to course B must NOT advance.
    event_a = event_factory(configuration=cert_configuration, course_id=COURSE_A, username=user.user_uid)
    dependencies_a = processor.process(achievement_rule_b, user, event_a)
    assert dependencies_a['is_achieved'] is False
    assert dependencies_a['events'][CERT_EVENT]['count'] == 0

    # Certificate in course B: the matching rule is now satisfied.
    event_b = event_factory(configuration=cert_configuration, course_id=COURSE_B, username=user.user_uid)
    dependencies_b = processor.process(achievement_rule_b, user, event_b)
    assert dependencies_b['is_achieved'] is True
    assert dependencies_b['events'][CERT_EVENT]['count'] == 1


def test_common_processor_counts_event_when_rule_has_no_course_filter(
    cert_configuration,
    rule_factory,
    achievement_rule_factory,
    event_factory,
    gamma_user_factory,
):
    """
    A rule without a course filter still counts any matching event (no behaviour change).
    """
    user = gamma_user_factory()
    rule = rule_factory(
        event_configuration=cert_configuration,
        action={CERT_EVENT: {'count': 1}},
        filters={},
    )
    achievement_rule = achievement_rule_factory(rule=rule, dependencies={})

    event = event_factory(configuration=cert_configuration, course_id=COURSE_A, username=user.user_uid)
    dependencies = CommonEventProcessor().process(achievement_rule, user, event)

    assert dependencies['is_achieved'] is True
    assert dependencies['events'][CERT_EVENT]['count'] == 1


def test_common_processor_counts_event_for_any_course_in_or_group(
    cert_configuration,
    rule_factory,
    achievement_rule_factory,
    event_factory,
    gamma_user_factory,
):
    """
    A rule whose course filter is a list (OR group) is satisfied by a cert in any listed course.
    """
    user = gamma_user_factory()
    rule = rule_factory(
        event_configuration=cert_configuration,
        action={CERT_EVENT: {'count': 1}},
        filters={'course': [COURSE_A, COURSE_B]},
    )
    achievement_rule = achievement_rule_factory(rule=rule, dependencies={})
    processor = CommonEventProcessor()

    # certificate in COURSE_B (listed) -> rule satisfied
    event_b = event_factory(configuration=cert_configuration, course_id=COURSE_B, username=user.user_uid)
    assert processor.process(achievement_rule, user, event_b)['is_achieved'] is True

    # certificate in an unlisted course -> not counted
    event_other = event_factory(configuration=cert_configuration, course_id='course-v1:org+X+1', username=user.user_uid)
    assert processor.process(achievement_rule, user, event_other)['is_achieved'] is False


DONE_EVENT = 'edx_done_toggled'


@pytest.fixture
def done_configuration(event_configuration_factory):
    return event_configuration_factory(event_type__name=DONE_EVENT)


def test_common_processor_counts_distinct_blocks_toward_block_set_rule(
    done_configuration,
    rule_factory,
    achievement_rule_factory,
    event_factory,
    gamma_user_factory,
):
    """
    A rule scoped to a set of "Mark as complete" blocks advances once per listed block.

    Blocks outside the set never advance it, partial progress keeps the canonical
    count/goal shape the dashboard circle renders (2 of 5 -> floor(2/5*100) = 40%),
    and completing the whole set achieves the rule. Each block can only count once
    in production because the event uid hashes (course, user, block) and duplicates
    are rejected at ingest.
    """
    user = gamma_user_factory()
    blocks = [f'block-v1:org+A+1+type@done+block@{suffix}' for suffix in 'abcde']
    rule = rule_factory(
        event_configuration=done_configuration,
        action={DONE_EVENT: {'count': 5}},
        filters={'course': COURSE_A, 'blocks': blocks},
    )
    achievement_rule = achievement_rule_factory(rule=rule, dependencies={})
    processor = CommonEventProcessor()

    def feed(block_id):
        event = event_factory(
            configuration=done_configuration,
            course_id=COURSE_A,
            username=user.user_uid,
            block_id=block_id,
        )
        dependencies = processor.process(achievement_rule, user, event)
        # what the use case persists between events (bulk_update of dependencies)
        achievement_rule.dependencies = dependencies
        achievement_rule.save()
        return dependencies

    # a done block in the same course but outside the set does not advance the rule
    dependencies = feed('block-v1:org+A+1+type@done+block@unrelated')
    assert dependencies['events'][DONE_EVENT]['count'] == 0
    assert dependencies['is_achieved'] is False

    feed(blocks[0])
    dependencies = feed(blocks[1])
    assert dependencies['events'][DONE_EVENT]['count'] == 2
    assert dependencies['events'][DONE_EVENT]['goal'] == 5
    assert dependencies['is_achieved'] is False

    for block_id in blocks[2:]:
        dependencies = feed(block_id)
    assert dependencies['events'][DONE_EVENT]['count'] == 5
    assert dependencies['is_achieved'] is True


def _block_set_rule(rule_factory, configuration, blocks):
    return rule_factory(
        event_configuration=configuration,
        action={DONE_EVENT: {'count': len(blocks)}},
        filters={'course': COURSE_A, 'blocks': blocks},
    )


def _day(n):
    return datetime(2026, 1, n, 12, tzinfo=utc)


def test_block_set_rule_credits_units_marked_before_the_rule_existed(
    done_configuration,
    rule_factory,
    achievement_rule_factory,
    event_factory,
    gamma_user_factory,
):
    """
    A learner who marked most of a section before the badge's rule (or their Achievement
    row) existed meets the goal by marking the one unit they had missed: progress comes
    from their history, not from a counter that only starts when the rule does.
    """
    user = gamma_user_factory()
    blocks = [f'block-v1:org+A+1+type@done+block@{suffix}' for suffix in 'abcde']
    rule = _block_set_rule(rule_factory, done_configuration, blocks)
    for day, block_id in enumerate(blocks[:4], start=1):
        event_factory(
            configuration=done_configuration, course_id=COURSE_A, username=user.user_uid,
            block_id=block_id, created_at=_day(day),
        )

    achievement_rule = achievement_rule_factory(rule=rule, dependencies={})
    missed_unit = event_factory(
        configuration=done_configuration, course_id=COURSE_A, username=user.user_uid,
        block_id=blocks[4], created_at=_day(9),
    )
    dependencies = CommonEventProcessor().process(achievement_rule, user, missed_unit)

    assert dependencies['is_achieved'] is True
    assert dependencies['events'][DONE_EVENT]['count'] == 5
    assert dependencies['events'][DONE_EVENT]['achieved_at'] == _day(9).isoformat()


def test_block_set_rule_is_met_by_whichever_unit_completes_the_set(
    done_configuration,
    rule_factory,
    achievement_rule_factory,
    event_factory,
    gamma_user_factory,
):
    """
    Units marked out of order count once each, even when one reached Gamma twice, and the
    goal is met by whichever unit completes the set. ``achieved_at`` is when the set was
    actually completed, also when history is replayed out of chronological order (a
    backfill walks source rows by id, not by date).
    """
    user = gamma_user_factory()
    blocks = [f'block-v1:org+A+1+type@done+block@{suffix}' for suffix in 'abcde']
    rule = _block_set_rule(rule_factory, done_configuration, blocks)
    achievement_rule = achievement_rule_factory(rule=rule, dependencies={})
    processor = CommonEventProcessor()

    def feed(block_id, day):
        event = event_factory(
            configuration=done_configuration, course_id=COURSE_A, username=user.user_uid,
            block_id=block_id, created_at=_day(day),
        )
        dependencies = processor.process(achievement_rule, user, event)
        achievement_rule.dependencies = dependencies
        achievement_rule.save()
        return dependencies

    # (unit, day it was marked) in replay order; unit "a" arrives a second time on day 7
    for block_id, day in ((blocks[3], 3), (blocks[0], 1), (blocks[0], 7), (blocks[4], 5), (blocks[1], 2)):
        dependencies = feed(block_id, day)
    assert dependencies['events'][DONE_EVENT]['count'] == 4
    assert dependencies['is_achieved'] is False
    assert 'achieved_at' not in dependencies['events'][DONE_EVENT]

    # the missed unit "c" (marked day 4) completes the set, which was whole once "e" was marked on day 5
    dependencies = feed(blocks[2], 4)
    assert dependencies['events'][DONE_EVENT]['count'] == 5
    assert dependencies['is_achieved'] is True
    assert dependencies['events'][DONE_EVENT]['achieved_at'] == _day(5).isoformat()


def test_block_set_rule_counts_a_unit_once_whichever_class_version_it_was_marked_in(
    done_configuration,
    rule_factory,
    achievement_rule_factory,
    event_factory,
    gamma_user_factory,
):
    """
    Units listed in two versions of a class: work begun in the older version carries over
    to the newer one, a unit marked in both versions counts once, and the goal is met, and
    dated, when the last unit is marked in either version.
    """
    older_course, newer_course = 'course-v1:org+A+2021', 'course-v1:org+A+2024'
    units = [
        [f'block-v1:org+A+2021+type@done+block@{suffix}', f'block-v1:org+A+2024+type@done+block@{suffix}']
        for suffix in 'abc'
    ]
    user = gamma_user_factory()
    rule = rule_factory(
        event_configuration=done_configuration,
        action={DONE_EVENT: {'count': len(units)}},
        filters={'course': [older_course, newer_course], 'blocks': units},
    )
    achievement_rule = achievement_rule_factory(rule=rule, dependencies={})
    processor = CommonEventProcessor()

    def feed(block_id, day):
        event = event_factory(
            configuration=done_configuration, username=user.user_uid, block_id=block_id, created_at=_day(day),
            course_id=older_course if '+2021+' in block_id else newer_course,
        )
        dependencies = processor.process(achievement_rule, user, event)
        achievement_rule.dependencies = dependencies
        achievement_rule.save()
        return dependencies['events'][DONE_EVENT], dependencies['is_achieved']

    assert feed(units[0][0], 1) == ({'goal': 3, 'count': 1, 'last_updated': _day(1).isoformat()}, False)
    assert feed(units[0][1], 2)[0]['count'] == 1           # the same unit again, in the newer version
    assert feed(units[1][0], 3)[0]['count'] == 2
    progress, achieved = feed(units[2][1], 4)              # the last unit, in the newer version
    assert achieved is True
    assert progress['count'] == 3
    assert progress['achieved_at'] == _day(4).isoformat()

"""
A section ("block-set") badge through the real event pipeline: signal -> badge backend -> completion.
"""
from datetime import datetime

import pytest
from django.contrib.contenttypes.models import ContentType
from django.utils.timezone import utc

from achievements.models import Achievement
from badges.models import Badge

pytestmark = pytest.mark.django_db

DONE_EVENT = 'edx_done_toggled'
COURSE = 'course-v1:org+A+1'
BLOCKS = [f'block-v1:org+A+1+type@done+block@{suffix}' for suffix in 'abcde']


def _day(n):
    return datetime(2026, 1, n, 12, tzinfo=utc)


@pytest.fixture
def done_configuration(event_configuration_factory):
    return event_configuration_factory(event_type__name=DONE_EVENT)


@pytest.fixture
def section_badge(done_configuration, rule_factory, badge_factory):
    rule = rule_factory(
        event_configuration=done_configuration,
        action={DONE_EVENT: {'count': len(BLOCKS)}},
        filters={'course': COURSE, 'blocks': BLOCKS},
    )
    return badge_factory(set_rules=rule, points=100)


def _mark_done(event_factory, configuration, user, block_id, **kwargs):
    return event_factory(
        configuration=configuration, username=user.user_uid, course_id=COURSE, block_id=block_id, **kwargs,
    )


def _achievement(badge, user):
    return Achievement.objects.filter(
        user=user, content_type=ContentType.objects.get_for_model(Badge), object_id=badge.id,
    ).first()


def test_section_badge_is_granted_when_the_skipped_unit_is_marked(
    section_badge, done_configuration, event_factory, gamma_user_factory,
):
    """
    A learner who skipped a unit and came back to it gets the badge, dated, at the
    moment the skipped unit is marked, not at the section's last unit.
    """
    user = gamma_user_factory()
    for block_id in BLOCKS[:2] + BLOCKS[3:]:
        _mark_done(event_factory, done_configuration, user, block_id)
    assert _achievement(section_badge, user).completed_at is None

    skipped_unit = _mark_done(event_factory, done_configuration, user, BLOCKS[2])

    achievement = _achievement(section_badge, user)
    assert achievement.all_rules_completed
    assert achievement.completed_at == skipped_unit.created_at
    assert achievement.completion_points_paid == 100


def test_replayed_history_dates_the_section_badge_when_it_was_earned(
    section_badge, done_configuration, event_factory, gamma_user_factory,
):
    """
    A backfill replays old clicks with their original times, in source-row order rather
    than date order. The badge is dated when the section was actually completed (the day
    its last unit was first marked), not when the replay got there.
    """
    user = gamma_user_factory()
    for block_id, day in zip(BLOCKS, (3, 1, 5, 2, 4)):
        _mark_done(event_factory, done_configuration, user, block_id, created_at=_day(day))

    achievement = _achievement(section_badge, user)
    assert achievement.all_rules_completed
    assert achievement.completed_at == _day(5)

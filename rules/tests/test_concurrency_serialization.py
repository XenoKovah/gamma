"""
Regression coverage for the per-user serialization of event processing.

True parallelism can't be reproduced under the sqlite test DB (no row locking,
and the suite isn't a TransactionTestCase), so these tests assert the two
properties the row lock exists to guarantee, by driving the events the way the
serialized outcome would: every same-user event's points accumulate, and a badge
whose rule a user already satisfies is created exactly once across repeated
events — never duplicated, never lost.
"""
import pytest
from django.contrib.contenttypes.models import ContentType

from achievements.models import Achievement
from badges.models import Badge
from events.enums import RggInternalEventTypes
from events.models import Event, EventConfiguration

pytestmark = pytest.mark.django_db

POINTS_EVENT = 'edx_grades_problem_submitted'


def badge_count(user, badge):
    return Achievement.objects.filter(
        user=user, content_type=ContentType.objects.get_for_model(Badge), object_id=badge.id,
    ).count()


def obtained_count(user):
    return Event.objects.filter(
        username=user.user_uid,
        configuration__event_type__name=RggInternalEventTypes.RGG_ACHIEVEMENT_OBTAINED.value,
    ).count()


@pytest.mark.enable_signals
def test_points_accumulate_across_events(
    event_configuration_factory, gamma_user_factory, event_factory,
):
    configuration = event_configuration_factory(event_type__name=POINTS_EVENT, award=5)
    user = gamma_user_factory(points=0)

    event_factory(configuration=configuration, username=user.user_uid)
    event_factory(configuration=configuration, username=user.user_uid)

    user.refresh_from_db()
    # Both events must count — no lost update.
    assert user.points == 10


@pytest.mark.enable_signals
def test_points_badge_created_once_across_repeated_events(
    event_configuration_factory,
    rule_factory,
    badge_factory,
    gamma_user_factory,
    event_factory,
):
    """
    A points-threshold badge the user already clears must be created exactly once
    and emit exactly one obtained event, no matter how many qualifying events
    arrive — the property the achievement-collision lock protects.
    """
    # The points-distribution config already exists (autouse setup_rgg_internal_events).
    points_config = EventConfiguration.objects.get(
        event_type__name=RggInternalEventTypes.RGG_POINTS_DISTRIBUTION.value,
    )
    earn_config = event_configuration_factory(event_type__name=POINTS_EVENT, award=5)
    rule = rule_factory(
        event_configuration=points_config,
        action={RggInternalEventTypes.RGG_POINTS_DISTRIBUTION.value: {'points': 5}},
        filters={},
    )
    badge = badge_factory(set_rules=rule)
    user = gamma_user_factory(points=0)

    for _ in range(3):
        event_factory(configuration=earn_config, username=user.user_uid)

    assert badge_count(user, badge) == 1
    assert obtained_count(user) == 1

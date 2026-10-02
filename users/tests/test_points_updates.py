"""
A user's points total stays correct, and the points-total rules ("Points points points!")
follow it, whichever path changes it.
"""
import pytest
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from achievements.models import Achievement
from achievements.usecases import AchievementCompletionUseCase
from badges.management.commands.process_anti_gaming import Command as AntiGamingCommand
from badges.models import Badge
from events.enums import RggInternalEventTypes
from events.models import EventConfiguration
from users.continuous_learning import DAILY_ACTIVE_POINTS

pytestmark = pytest.mark.django_db

POINTS_EVENT = RggInternalEventTypes.RGG_POINTS_DISTRIBUTION.value
OBTAINED_EVENT = RggInternalEventTypes.RGG_ACHIEVEMENT_OBTAINED.value
BOOKMARK = 'edx_bookmark_added'


def after_commit():
    """
    Run the on-commit callbacks queued inside the block; the test's own transaction never commits.
    """
    return TestCase.captureOnCommitCallbacks(execute=True)


@pytest.fixture
def points_badge(rule_factory, badge_factory):
    """
    A 0-point badge for a lifetime total of 100 points, like the "Points points points!" ladder.
    """
    configuration = EventConfiguration.objects.get(event_type__name=POINTS_EVENT)
    rule = rule_factory(event_configuration=configuration, action={POINTS_EVENT: {'points': 100}}, filters={})
    return badge_factory(set_rules=rule, points=0)


@pytest.fixture
def bookmark_configuration(event_configuration_factory):
    return event_configuration_factory(event_type__name=BOOKMARK, award=5)


def ring(user, badge):
    """
    The user's progress on a one-rule badge as (count, goal, earned), or None with no achievement.
    """
    achievement = Achievement.objects.filter(
        user=user, content_type=ContentType.objects.get_for_model(Badge), object_id=badge.id,
    ).first()
    if achievement is None:
        return None
    progress = achievement.achievement_rules.get().dependencies['events'][POINTS_EVENT]
    return progress['count'], progress['goal'], achievement.completed_at is not None


def emit_points_distribution(user):
    with after_commit():
        user.refresh_points_progress()


def test_a_negative_total_shows_no_progress(points_badge, gamma_user_factory):
    """
    Penalty badges can push the total below zero; the ring must not render as e.g. -474%.
    """
    user = gamma_user_factory(points=-9474)

    emit_points_distribution(user)

    assert ring(user, points_badge) == (0, 100, False)


def test_the_refresh_waits_for_the_transaction_to_commit(points_badge, gamma_user_factory):
    user = gamma_user_factory(points=150)

    with after_commit() as callbacks:
        user.refresh_points_progress()
        assert ring(user, points_badge) is None

    assert len(callbacks) == 1
    assert ring(user, points_badge) == (150, 100, True)


def test_backfills_can_skip_the_refresh(points_badge, badge_factory, gamma_user_factory, settings):
    """
    RGG_SKIP_POINTS_REFRESH (set only in backfill processes) defers the re-check to the backfill's final pass.
    """
    settings.RGG_SKIP_POINTS_REFRESH = True
    user = gamma_user_factory(points=0)

    with after_commit():
        badge_factory(points=150).award_to_user(user)
        user.refresh_points_progress()

    user.refresh_from_db()
    assert user.points == 150
    assert ring(user, points_badge) is None


def test_a_manual_grant_reaches_the_points_badges(points_badge, badge_factory, gamma_user_factory):
    user = gamma_user_factory(points=0)

    with after_commit():
        badge_factory(points=150).award_to_user(user)

    assert ring(user, points_badge) == (150, 100, True)


def test_revoking_a_grant_lowers_the_points_ring(points_badge, badge_factory, gamma_user_factory):
    user = gamma_user_factory(points=0)
    granted = badge_factory(points=60)
    with after_commit():
        granted.award_to_user(user)
    assert ring(user, points_badge) == (60, 100, False)

    with after_commit():
        granted.revoke_from_user(user)

    user.refresh_from_db()
    assert user.points == 0
    assert ring(user, points_badge) == (0, 100, False)


def test_a_badge_payout_outside_the_event_pipeline_reaches_the_points_badges(
    points_badge, badge_factory, achievement_factory, gamma_user_factory,
):
    """
    E.g. a badge granted by recompute, or completed by an internal (no-points) event.
    """
    user = gamma_user_factory(points=0)
    badge = badge_factory(points=150)
    achievement = achievement_factory(
        user=user, content_type=ContentType.objects.get_for_model(Badge), object_id=badge.id, completed_at=None,
    )

    with after_commit():
        AchievementCompletionUseCase().execute(achievement)

    assert ring(user, points_badge) == (150, 100, True)


@pytest.mark.parametrize('docked_before, dock, expected_points', [(0, 30, 90), (30, 0, 150)], ids=['dock', 'restore'])
def test_an_anti_gaming_change_moves_the_points_ring(
    rule_factory, badge_factory, gamma_user_factory, docked_before, dock, expected_points,
):
    configuration = EventConfiguration.objects.get(event_type__name=POINTS_EVENT)
    goal_200 = badge_factory(
        set_rules=rule_factory(event_configuration=configuration, action={POINTS_EVENT: {'points': 200}}, filters={}),
        points=0,
    )
    user = gamma_user_factory(points=120)
    course_id = 'course-v1:org+A+1'
    if docked_before:
        user.anti_gaming_penalties.create(course_id=course_id, points_docked=docked_before)

    with after_commit():
        if dock:
            AntiGamingCommand()._apply(  # pylint: disable=protected-access
                user, course_id, dock, rushed_blocks=6, longest=12, mode='dock',
            )
        else:
            AntiGamingCommand()._clear(user, course_id)  # pylint: disable=protected-access

    user.refresh_from_db()
    assert user.points == expected_points
    assert ring(user, goal_200) == (expected_points, 200, False)


def test_the_daily_continuous_learning_points_reach_the_points_ring(
    points_badge, bookmark_configuration, gamma_user_factory, event_factory, settings,
):
    """
    The daily points are added after the event pipeline has already re-evaluated the ring.
    """
    settings.RGG_CONTINUOUS_LEARNING_ENABLED = True
    user = gamma_user_factory(points=0)

    with after_commit():
        event_factory(configuration=bookmark_configuration, username=user.user_uid)

    user.refresh_from_db()
    assert user.points == 5 + DAILY_ACTIVE_POINTS
    assert ring(user, points_badge) == (5 + DAILY_ACTIVE_POINTS, 100, False)


def test_a_badge_completed_on_a_later_event_keeps_its_points(
    bookmark_configuration, rule_factory, badge_factory, gamma_user_factory, event_factory,
):
    """
    The completion payout went through a second copy of the user that the pipeline then overwrote.
    """
    rule = rule_factory(event_configuration=bookmark_configuration, action={BOOKMARK: {'count': 2}}, filters={})
    badge_factory(set_rules=rule, points=100)
    user = gamma_user_factory(points=0)

    event_factory(configuration=bookmark_configuration, username=user.user_uid)
    event_factory(configuration=bookmark_configuration, username=user.user_uid)

    user.refresh_from_db()
    assert user.points == 5 + 5 + 100
    assert sum(day['points'] for days in user.progress.values() for day in days) == 110


def test_a_badge_completed_inside_another_badges_event_keeps_its_points(
    bookmark_configuration, rule_factory, badge_factory, gamma_user_factory, event_factory,
):
    """
    The dependent badge completes in a nested internal event that holds its own copy of the user.
    """
    first = badge_factory(
        set_rules=rule_factory(event_configuration=bookmark_configuration, action={BOOKMARK: {'count': 1}}, filters={}),
        points=0,
    )
    obtained = EventConfiguration.objects.get(event_type__name=OBTAINED_EVENT)
    badge_factory(
        set_rules=rule_factory(
            event_configuration=obtained,
            action={OBTAINED_EVENT: {'dependent_object_id': first.id, 'dependent_content_type': 'badge'}},
            filters={},
        ),
        points=150,
    )
    user = gamma_user_factory(points=0)

    event_factory(configuration=bookmark_configuration, username=user.user_uid)

    user.refresh_from_db()
    assert user.points == 5 + 150

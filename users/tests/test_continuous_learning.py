"""Tests for the Continuous Learning daily-points + consecutive-day streak engine."""
from datetime import date, timedelta

import pytest
from django.contrib.contenttypes.models import ContentType

from achievements.models import Achievement
from badges.models import Badge
from users.continuous_learning import (
    CONTINUOUS_LEARNING_KEY,
    CONTINUOUS_LEARNING_TITLE,
    DAILY_ACTIVE_POINTS,
    register_active_day,
    streak_badge_slug,
)

pytestmark = pytest.mark.django_db

DAY = date(2026, 6, 1)


@pytest.fixture(autouse=True)
def _enable_continuous_learning(settings):
    """Continuous Learning is off by default in test settings; turn it on for these tests."""
    settings.RGG_CONTINUOUS_LEARNING_ENABLED = True


def _bucket(user):
    return (user.chart or {}).get(CONTINUOUS_LEARNING_KEY, {'points': 0})


def _achievement_count(user, badge):
    return Achievement.objects.filter(
        user=user, content_type=ContentType.objects.get_for_model(Badge), object_id=badge.id,
    ).count()


def test_first_active_day_starts_streak_and_awards_daily_points(gamma_user_factory):
    user = gamma_user_factory(points=0, chart={}, current_streak=0, last_active_date=None)

    assert register_active_day(user, activity_date=DAY) is True
    user.refresh_from_db()

    assert user.current_streak == 1
    assert user.last_active_date == DAY
    assert user.points == DAILY_ACTIVE_POINTS
    assert _bucket(user)['points'] == DAILY_ACTIVE_POINTS
    assert _bucket(user)['title'] == CONTINUOUS_LEARNING_TITLE
    # Daily points are credited to the activity day on the progress timeline.
    assert user.progress[str(DAY.year)][0]['points'] == DAILY_ACTIVE_POINTS


def test_second_event_same_day_is_noop(gamma_user_factory):
    user = gamma_user_factory(points=0, chart={}, current_streak=0, last_active_date=None)

    register_active_day(user, activity_date=DAY)
    assert register_active_day(user, activity_date=DAY) is False
    user.refresh_from_db()

    assert user.current_streak == 1
    assert user.points == DAILY_ACTIVE_POINTS  # not doubled


def test_consecutive_days_increment_streak(gamma_user_factory):
    user = gamma_user_factory(points=0, chart={}, current_streak=0, last_active_date=None)

    register_active_day(user, activity_date=DAY)
    register_active_day(user, activity_date=DAY + timedelta(days=1))
    user.refresh_from_db()

    assert user.current_streak == 2
    assert user.points == 2 * DAILY_ACTIVE_POINTS
    assert _bucket(user)['points'] == 2 * DAILY_ACTIVE_POINTS


def test_gap_resets_streak_to_one(gamma_user_factory):
    user = gamma_user_factory(points=0, chart={}, current_streak=0, last_active_date=None)

    register_active_day(user, activity_date=DAY)
    register_active_day(user, activity_date=DAY + timedelta(days=1))
    # Skip a day -> streak breaks.
    register_active_day(user, activity_date=DAY + timedelta(days=3))
    user.refresh_from_db()

    assert user.current_streak == 1
    # Every active day still earns the daily points (3 active days here).
    assert user.points == 3 * DAILY_ACTIVE_POINTS


def test_passive_vote_event_does_not_count(gamma_user_factory):
    user = gamma_user_factory(points=0, chart={}, current_streak=0, last_active_date=None)

    assert register_active_day(user, event_name='edx_forum_thread_voted', activity_date=DAY) is False
    user.refresh_from_db()

    assert user.current_streak == 0
    assert user.points == 0
    assert _bucket(user)['points'] == 0


def test_disabled_feature_is_noop(gamma_user_factory, settings):
    settings.RGG_CONTINUOUS_LEARNING_ENABLED = False
    user = gamma_user_factory(points=0, chart={}, current_streak=0, last_active_date=None)

    assert register_active_day(user, activity_date=DAY) is False
    user.refresh_from_db()

    assert user.current_streak == 0
    assert user.points == 0


def test_reaching_milestone_awards_badge_and_bonus(gamma_user_factory, badge_factory):
    bonus = 10
    badge = badge_factory(title='5 day streak', slug=streak_badge_slug(5), points=bonus)
    user = gamma_user_factory(points=0, chart={}, current_streak=0, last_active_date=None)

    for offset in range(5):
        register_active_day(user, activity_date=DAY + timedelta(days=offset))
    user.refresh_from_db()

    assert user.current_streak == 5
    assert badge.has_achievement(user) is True
    # 5 active days * 5 daily points + 10 milestone bonus.
    expected = 5 * DAILY_ACTIVE_POINTS + bonus
    assert user.points == expected
    assert _bucket(user)['points'] == expected


def test_milestone_badge_not_re_awarded_after_streak_breaks_and_reclimbs(gamma_user_factory, badge_factory):
    bonus = 10
    badge = badge_factory(title='5 day streak', slug=streak_badge_slug(5), points=bonus)
    user = gamma_user_factory(points=0, chart={}, current_streak=0, last_active_date=None)

    # First 5-day run earns the badge once.
    for offset in range(5):
        register_active_day(user, activity_date=DAY + timedelta(days=offset))
    # Break, then climb to 5 again.
    for offset in range(10, 15):
        register_active_day(user, activity_date=DAY + timedelta(days=offset))
    user.refresh_from_db()

    assert badge.has_achievement(user) is True
    assert _achievement_count(user, badge) == 1  # earned once, never re-awarded
    # 10 active days * 5 daily + exactly one 10 bonus (not two).
    assert user.points == 10 * DAILY_ACTIVE_POINTS + bonus
    assert _bucket(user)['points'] == 10 * DAILY_ACTIVE_POINTS + bonus


def test_higher_milestone_skipped_when_badge_row_absent(gamma_user_factory, badge_factory):
    # Only the 5-day badge exists; reaching 5 must not error on the missing 10/20/30 rows.
    badge_factory(title='5 day streak', slug=streak_badge_slug(5), points=10)
    user = gamma_user_factory(points=0, chart={}, current_streak=0, last_active_date=None)

    for offset in range(6):
        register_active_day(user, activity_date=DAY + timedelta(days=offset))
    user.refresh_from_db()

    assert user.current_streak == 6
    assert user.points == 6 * DAILY_ACTIVE_POINTS + 10


@pytest.mark.enable_signals
def test_common_event_through_signal_registers_active_day(
    gamma_user_factory, event_configuration_factory, event_factory,
):
    """End-to-end: a common point-earning Event fires the signal and credits an active day."""
    user = gamma_user_factory(points=0, chart={}, current_streak=0, last_active_date=None)
    configuration = event_configuration_factory(event_type__name='edx_done_toggled', award=5)

    event_factory(configuration=configuration, username=user.user_uid)
    user.refresh_from_db()

    assert user.current_streak == 1
    assert _bucket(user)['points'] == DAILY_ACTIVE_POINTS
    # Event award (5) + daily Continuous Learning award (5).
    assert user.points == 5 + DAILY_ACTIVE_POINTS

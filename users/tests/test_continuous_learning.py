"""Tests for the Continuous Learning daily-points + consecutive-day streak engine."""
from datetime import date, timedelta

import pytest
from django.contrib.contenttypes.models import ContentType
from django.core.management import call_command

from achievements.models import Achievement
from badges.models import Badge
from users.continuous_learning import (
    CONTINUOUS_LEARNING_KEY,
    CONTINUOUS_LEARNING_TITLE,
    DAILY_ACTIVE_POINTS,
    register_active_day,
    reset_stale_streaks,
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


def _streak_progress_count(user, badge):
    """The in-progress streak count the dashboard ring reads (achievement dependency)."""
    ach = Achievement.objects.filter(
        user=user, content_type=ContentType.objects.get_for_model(Badge), object_id=badge.id,
    ).first()
    if ach is None:
        return None
    for dep in ach.achievement_dependencies or []:
        event = (dep.get('events') or {}).get('rgg_continuous_learning_streak')
        if event is not None:
            return event.get('count')
    return None


def _register_days(user_pk, n, start=DAY):
    """Drive n consecutive active days, fetching a fresh instance per day as the live
    signal does for each event (avoids a stale instance clobbering completion bonuses)."""
    from users.models import GammaUser
    for offset in range(n):
        register_active_day(GammaUser.objects.get(pk=user_pk), activity_date=start + timedelta(days=offset))


def test_streak_badge_awarded_and_progress_via_rules_engine(gamma_user_factory):
    # The real deploy path: seed the streak event type + the 4 rule-driven badges.
    call_command('initialize_continuous_learning_badges')
    user = gamma_user_factory(points=0, chart={}, current_streak=0, last_active_date=None)

    _register_days(user.pk, 5)  # 5 consecutive active days
    user.refresh_from_db()

    badge5 = Badge.objects.get(slug=streak_badge_slug(5))
    badge10 = Badge.objects.get(slug=streak_badge_slug(10))

    assert user.current_streak == 5
    # 5-day badge awarded by the rules engine.
    assert badge5.has_achievement(user) is True
    # Bonus (Badge.points=10) goes to the total, NOT the Continuous Learning bucket;
    # the bucket holds only the daily points (5 days * 5).
    assert _bucket(user)['points'] == 5 * DAILY_ACTIVE_POINTS
    assert user.points == 5 * DAILY_ACTIVE_POINTS + 10
    # 10-day badge is in progress with the ring data reading current_streak (5/10).
    assert badge10.has_achievement(user) is True
    assert _streak_progress_count(user, badge10) == 5


def test_streak_badge_awarded_exactly_once(gamma_user_factory):
    call_command('initialize_continuous_learning_badges')
    user = gamma_user_factory(points=0, chart={}, current_streak=0, last_active_date=None)

    _register_days(user.pk, 10)  # reach the 10-day milestone
    user.refresh_from_db()

    badge5 = Badge.objects.get(slug=streak_badge_slug(5))
    badge10 = Badge.objects.get(slug=streak_badge_slug(10))

    assert badge5.has_achievement(user) and badge10.has_achievement(user)
    assert _achievement_count(user, badge5) == 1  # not duplicated as the streak climbs past 5
    # 10 daily*5 + 5-day(10) + 10-day(10) bonuses; bucket holds only the daily points.
    assert user.points == 10 * DAILY_ACTIVE_POINTS + 10 + 10
    assert _bucket(user)['points'] == 10 * DAILY_ACTIVE_POINTS


def test_reset_stale_streaks_zeros_broken_streak_and_ring(gamma_user_factory):
    call_command('initialize_continuous_learning_badges')
    user = gamma_user_factory(points=0, chart={}, current_streak=0, last_active_date=None)
    _register_days(user.pk, 3)  # active DAY, DAY+1, DAY+2 -> streak 3
    user.refresh_from_db()
    badge5 = Badge.objects.get(slug=streak_badge_slug(5))
    assert user.current_streak == 3 and _streak_progress_count(user, badge5) == 3

    # Two days later (missed DAY+3) -> streak broken.
    reset = reset_stale_streaks(today=DAY + timedelta(days=4))
    user.refresh_from_db()

    assert reset == 1
    assert user.current_streak == 0
    assert _streak_progress_count(user, badge5) == 0  # ring dropped to 0%
    assert user.points == 3 * DAILY_ACTIVE_POINTS  # earned points are untouched


def test_reset_leaves_streak_active_yesterday_alone(gamma_user_factory):
    call_command('initialize_continuous_learning_badges')
    user = gamma_user_factory(points=0, chart={}, current_streak=0, last_active_date=None)
    _register_days(user.pk, 3)  # last active = DAY+2

    # "Today" is the day right after the last active day: the streak is still continuable.
    reset = reset_stale_streaks(today=DAY + timedelta(days=3))
    user.refresh_from_db()

    assert reset == 0
    assert user.current_streak == 3  # preserved


def test_reset_is_noop_when_disabled(gamma_user_factory, settings):
    user = gamma_user_factory(points=0, chart={}, current_streak=3, last_active_date=DAY)
    settings.RGG_CONTINUOUS_LEARNING_ENABLED = False

    assert reset_stale_streaks(today=DAY + timedelta(days=4)) == 0
    user.refresh_from_db()
    assert user.current_streak == 3


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

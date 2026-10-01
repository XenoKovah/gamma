"""Tests for the per-learner Continuous Learning streak-badge backfill."""
from datetime import date, datetime, timedelta, timezone as dt_timezone

import pytest
from django.contrib.contenttypes.models import ContentType
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db.models.signals import post_save
from factory.django import mute_signals

from achievements.models import Achievement, AchievementRule
from badges.models import Badge
from users.continuous_learning import (
    CONTINUOUS_LEARNING_KEY,
    DAILY_STREAK,
    WEEKDAY_STREAK,
    milestones_reached,
    register_active_day,
)
from users.models import GammaUser

pytestmark = pytest.mark.django_db

# A Monday, so DAY+4 is Friday, DAY+5/DAY+6 the weekend and DAY+7 the next Monday.
DAY = date(2026, 6, 1)


@pytest.fixture(autouse=True)
def _enable_continuous_learning(settings):
    settings.RGG_CONTINUOUS_LEARNING_ENABLED = True


@pytest.fixture
def done_configuration(event_configuration_factory):
    return event_configuration_factory(event_type__name='edx_done_toggled', award=5)


def _new_user(gamma_user_factory):
    return gamma_user_factory(
        points=0, chart={}, progress={},
        current_streak=0, last_active_date=None,
        current_weekday_streak=0, last_weekday_active_date=None,
    )


def _active_on(event_factory, configuration, user, days):
    """
    Historical point-earning events, two per day (the backfill must count days, not events).

    Created with the event signal muted: they stand for history that predates the feature,
    so the live engine must not process them as they are inserted.
    """
    with mute_signals(post_save):
        _insert_events(event_factory, configuration, user, days)


def _insert_events(event_factory, configuration, user, days):
    for day in days:
        for hour in (9, 15):
            event_factory(
                configuration=configuration, username=user.user_uid,
                created_at=datetime(day.year, day.month, day.day, hour, tzinfo=dt_timezone.utc),
            )


def _consecutive(n, start=DAY):
    return [start + timedelta(days=offset) for offset in range(n)]


def _achievement(user, kind, days):
    badge = Badge.objects.get(slug=kind.badge_slug(days))
    return Achievement.objects.filter(
        user=user, content_type=ContentType.objects.get_for_model(Badge), object_id=badge.id,
    ).first()


def _earned(user, kind, days):
    achievement = _achievement(user, kind, days)
    return achievement is not None and achievement.completed_at is not None


def test_milestones_reached_dates_each_milestone_by_its_first_run():
    # A 7-day run, a gap, then a 12-day run: 5 is first reached in the first run, 10 only in the second.
    first = _consecutive(7)
    second = _consecutive(12, start=DAY + timedelta(days=9))

    assert milestones_reached(first + second, DAILY_STREAK) == {5: first[4], 10: second[9]}


def test_milestones_reached_weekday_kind_bridges_weekends():
    weekdays = [day for day in _consecutive(14) if WEEKDAY_STREAK.counts(day)]  # two Mon-Fri weeks

    assert milestones_reached(weekdays, WEEKDAY_STREAK) == {5: weekdays[4], 10: weekdays[9]}
    # The calendar kind sees the weekend as a gap, so it never passes 5.
    assert milestones_reached(weekdays, DAILY_STREAK) == {5: weekdays[4]}


def test_dry_run_writes_nothing(gamma_user_factory, event_factory, done_configuration):
    call_command('initialize_continuous_learning_badges')
    user = _new_user(gamma_user_factory)
    _active_on(event_factory, done_configuration, user, _consecutive(6))

    call_command('backfill_continuous_learning')

    user.refresh_from_db()
    assert user.points == 0
    assert _achievement(user, DAILY_STREAK, 5) is None


def test_commit_grants_reached_milestones_without_replaying(gamma_user_factory, event_factory, done_configuration):
    call_command('initialize_continuous_learning_badges')
    user = _new_user(gamma_user_factory)
    days = _consecutive(6)  # Mon..Sat: 6 calendar days, 5 weekdays
    _active_on(event_factory, done_configuration, user, days)

    call_command('backfill_continuous_learning', '--commit')
    user.refresh_from_db()

    assert _earned(user, DAILY_STREAK, 5)
    assert _earned(user, WEEKDAY_STREAK, 5)
    assert not _earned(user, DAILY_STREAK, 10)
    # Only the two badges' completion points: no daily +5s and no bucket.
    assert user.points == 10 + 10
    assert CONTINUOUS_LEARNING_KEY not in (user.chart or {})
    # Streak counters are left for the live engine.
    assert (user.current_streak, user.last_active_date) == (0, None)
    assert (user.current_weekday_streak, user.last_weekday_active_date) == (0, None)

    achievement = _achievement(user, DAILY_STREAK, 5)
    assert achievement.completed_at.date() == days[4]  # dated when the milestone was reached
    assert achievement.completion_points_paid == 10
    assert achievement.notification_seen_at is not None  # silent by default
    assert set(achievement.achievement_rules.values_list('status', flat=True)) == {AchievementRule.Statuses.COMPLETED}


def test_notify_leaves_the_notification_pending(gamma_user_factory, event_factory, done_configuration):
    call_command('initialize_continuous_learning_badges')
    user = _new_user(gamma_user_factory)
    _active_on(event_factory, done_configuration, user, _consecutive(5))

    call_command('backfill_continuous_learning', '--commit', '--notify')

    assert _achievement(user, DAILY_STREAK, 5).notification_seen_at is None


def test_completes_the_live_in_progress_ring_in_place(gamma_user_factory, event_factory, done_configuration):
    call_command('initialize_continuous_learning_badges')
    user = _new_user(gamma_user_factory)
    _active_on(event_factory, done_configuration, user, _consecutive(5))
    # The live engine already tracks a 1-day streak, so every streak badge has an in-progress row.
    today = DAY + timedelta(days=30)
    register_active_day(GammaUser.objects.get(pk=user.pk), activity_date=today)
    assert _achievement(user, DAILY_STREAK, 5).completed_at is None

    call_command('backfill_continuous_learning', '--commit')
    user.refresh_from_db()

    badge = Badge.objects.get(slug=DAILY_STREAK.badge_slug(5))
    assert Achievement.objects.filter(user=user, object_id=badge.id).count() == 1
    assert _earned(user, DAILY_STREAK, 5)
    assert user.current_streak == 1 and user.last_active_date == today  # live state untouched


def test_rerun_and_live_engine_never_pay_twice(gamma_user_factory, event_factory, done_configuration):
    call_command('initialize_continuous_learning_badges')
    user = _new_user(gamma_user_factory)
    _active_on(event_factory, done_configuration, user, _consecutive(5))

    call_command('backfill_continuous_learning', '--commit')
    call_command('backfill_continuous_learning', '--commit')
    user.refresh_from_db()
    assert user.points == 10 + 10

    # Five more live days later on: the already-earned 5-day badges must not pay again.
    start = DAY + timedelta(days=28)  # a Monday
    for day in _consecutive(5, start=start):
        register_active_day(GammaUser.objects.get(pk=user.pk), activity_date=day)
    user.refresh_from_db()
    assert user.points == 10 + 10 + 5 * 5


def test_shards_partition_the_learners(gamma_user_factory, event_factory, done_configuration):
    call_command('initialize_continuous_learning_badges')
    users = [_new_user(gamma_user_factory) for _ in range(4)]
    for user in users:
        _active_on(event_factory, done_configuration, user, _consecutive(5))

    call_command('backfill_continuous_learning', '--commit', '--shard', '1/2', '--batch-size', '1')
    assert {u.pk for u in users if _earned(u, DAILY_STREAK, 5)} == {u.pk for u in users if u.pk % 2 == 1}

    call_command('backfill_continuous_learning', '--commit', '--shard', '0/2')
    assert all(_earned(u, DAILY_STREAK, 5) for u in users)


def test_passive_events_do_not_count(gamma_user_factory, event_factory, event_configuration_factory):
    call_command('initialize_continuous_learning_badges')
    user = _new_user(gamma_user_factory)
    vote = event_configuration_factory(event_type__name='edx_forum_thread_voted', award=2)
    _active_on(event_factory, vote, user, _consecutive(5))

    call_command('backfill_continuous_learning', '--commit')

    assert _achievement(user, DAILY_STREAK, 5) is None


@pytest.mark.parametrize('spec', ['2/2', 'x', '1/0'])
def test_bad_shard_is_rejected(spec):
    with pytest.raises(CommandError):
        call_command('backfill_continuous_learning', '--shard', spec)

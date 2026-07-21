"""Tests for the Continuous Learning daily-points + streak engine (daily and weekday)."""
from datetime import date, timedelta

import pytest
from django.contrib.contenttypes.models import ContentType
from django.core.files.base import ContentFile
from django.core.management import call_command

from achievements.models import Achievement
from badges.models import Badge
from users.continuous_learning import (
    CONTINUOUS_LEARNING_KEY,
    CONTINUOUS_LEARNING_TITLE,
    DAILY_ACTIVE_POINTS,
    DAILY_STREAK,
    WEEKDAY_STREAK,
    register_active_day,
    reset_stale_streaks,
)

pytestmark = pytest.mark.django_db

# A Monday, so the offsets below line up with the working week: DAY+4 is Friday,
# DAY+5/DAY+6 the weekend, DAY+7 the next Monday.
DAY = date(2026, 6, 1)
FRIDAY = DAY + timedelta(days=4)
SATURDAY = DAY + timedelta(days=5)
SUNDAY = DAY + timedelta(days=6)
NEXT_MONDAY = DAY + timedelta(days=7)


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


def _new_user(gamma_user_factory):
    return gamma_user_factory(
        points=0, chart={},
        current_streak=0, last_active_date=None,
        current_weekday_streak=0, last_weekday_active_date=None,
    )


def test_first_active_day_starts_streak_and_awards_daily_points(gamma_user_factory):
    user = _new_user(gamma_user_factory)

    assert register_active_day(user, activity_date=DAY) is True
    user.refresh_from_db()

    assert user.current_streak == 1
    assert user.last_active_date == DAY
    # DAY is a Monday, so it starts the weekday run too.
    assert user.current_weekday_streak == 1
    assert user.last_weekday_active_date == DAY
    # One active day earns the daily points once, however many runs it advances.
    assert user.points == DAILY_ACTIVE_POINTS
    assert _bucket(user)['points'] == DAILY_ACTIVE_POINTS
    assert _bucket(user)['title'] == CONTINUOUS_LEARNING_TITLE
    # Daily points are credited to the activity day on the progress timeline.
    assert user.progress[str(DAY.year)][0]['points'] == DAILY_ACTIVE_POINTS


def test_second_event_same_day_is_noop(gamma_user_factory):
    user = _new_user(gamma_user_factory)

    register_active_day(user, activity_date=DAY)
    assert register_active_day(user, activity_date=DAY) is False
    user.refresh_from_db()

    assert user.current_streak == 1
    assert user.current_weekday_streak == 1
    assert user.points == DAILY_ACTIVE_POINTS  # not doubled


def test_consecutive_days_increment_streak(gamma_user_factory):
    user = _new_user(gamma_user_factory)

    register_active_day(user, activity_date=DAY)
    register_active_day(user, activity_date=DAY + timedelta(days=1))
    user.refresh_from_db()

    assert user.current_streak == 2
    assert user.current_weekday_streak == 2  # Mon + Tue
    assert user.points == 2 * DAILY_ACTIVE_POINTS
    assert _bucket(user)['points'] == 2 * DAILY_ACTIVE_POINTS


def test_gap_resets_streak_to_one(gamma_user_factory):
    user = _new_user(gamma_user_factory)

    register_active_day(user, activity_date=DAY)
    register_active_day(user, activity_date=DAY + timedelta(days=1))
    # Skip a day -> streak breaks. All three days are weekdays, so both runs break.
    register_active_day(user, activity_date=DAY + timedelta(days=3))
    user.refresh_from_db()

    assert user.current_streak == 1
    assert user.current_weekday_streak == 1
    # Every active day still earns the daily points (3 active days here).
    assert user.points == 3 * DAILY_ACTIVE_POINTS


def test_passive_vote_event_does_not_count(gamma_user_factory):
    user = _new_user(gamma_user_factory)

    assert register_active_day(user, event_name='edx_forum_thread_voted', activity_date=DAY) is False
    user.refresh_from_db()

    assert user.current_streak == 0
    assert user.current_weekday_streak == 0
    assert user.points == 0
    assert _bucket(user)['points'] == 0


def test_disabled_feature_is_noop(gamma_user_factory, settings):
    settings.RGG_CONTINUOUS_LEARNING_ENABLED = False
    user = _new_user(gamma_user_factory)

    assert register_active_day(user, activity_date=DAY) is False
    user.refresh_from_db()

    assert user.current_streak == 0
    assert user.current_weekday_streak == 0
    assert user.points == 0


# --------------------------------------------------------------------------------------
# Weekday streaks: the run a Mon-Fri learner keeps across the weekend.
# --------------------------------------------------------------------------------------


def test_weekday_streak_bridges_the_weekend(gamma_user_factory):
    """Friday -> Monday continues the weekday run, while the calendar-day run resets."""
    user = _new_user(gamma_user_factory)

    _register_days(user.pk, 5)  # Mon-Fri
    user.refresh_from_db()  # _register_days advanced the row, not this instance
    register_active_day(user, activity_date=NEXT_MONDAY)
    user.refresh_from_db()

    assert user.current_weekday_streak == 6
    assert user.last_weekday_active_date == NEXT_MONDAY
    # The calendar-day run broke over the weekend — precisely the gap this kind closes.
    assert user.current_streak == 1


def test_weekend_activity_leaves_the_weekday_streak_untouched(gamma_user_factory):
    """A Saturday neither extends the weekday run nor breaks it; it just isn't counted."""
    user = _new_user(gamma_user_factory)

    register_active_day(user, activity_date=FRIDAY)
    register_active_day(user, activity_date=SATURDAY)
    user.refresh_from_db()

    assert user.current_weekday_streak == 1
    assert user.last_weekday_active_date == FRIDAY  # not advanced onto the Saturday
    assert user.current_streak == 2
    # The weekend day is still an active day for points, just not for the weekday run.
    assert user.points == 2 * DAILY_ACTIVE_POINTS


def test_weekend_only_activity_never_starts_a_weekday_streak(gamma_user_factory):
    user = _new_user(gamma_user_factory)

    register_active_day(user, activity_date=SATURDAY)
    register_active_day(user, activity_date=SUNDAY)
    user.refresh_from_db()

    assert user.current_weekday_streak == 0
    assert user.last_weekday_active_date is None
    assert user.current_streak == 2


def test_missed_weekday_breaks_the_weekday_streak(gamma_user_factory):
    user = _new_user(gamma_user_factory)

    register_active_day(user, activity_date=DAY)                      # Mon
    register_active_day(user, activity_date=DAY + timedelta(days=1))  # Tue
    register_active_day(user, activity_date=DAY + timedelta(days=3))  # Thu, skipping Wed
    user.refresh_from_db()

    assert user.current_weekday_streak == 1


def _streak_progress_count(user, badge, kind=DAILY_STREAK):
    """The in-progress streak count the dashboard ring reads (achievement dependency)."""
    ach = Achievement.objects.filter(
        user=user, content_type=ContentType.objects.get_for_model(Badge), object_id=badge.id,
    ).first()
    if ach is None:
        return None
    for dep in ach.achievement_dependencies or []:
        event = (dep.get('events') or {}).get(kind.event_name)
        if event is not None:
            return event.get('count')
    return None


def _register_days(user_pk, n, start=DAY):
    """Drive n consecutive active days, fetching a fresh instance per day as the live
    signal does for each event (avoids a stale instance clobbering completion bonuses)."""
    from users.models import GammaUser
    for offset in range(n):
        register_active_day(GammaUser.objects.get(pk=user_pk), activity_date=start + timedelta(days=offset))


def _register_weekdays(user_pk, n, start=DAY):
    """Drive n consecutive active *weekdays*, skipping the weekends entirely — the
    Mon-Fri learner this feature exists for."""
    from users.models import GammaUser
    day, registered = start, 0
    while registered < n:
        if WEEKDAY_STREAK.counts(day):
            register_active_day(GammaUser.objects.get(pk=user_pk), activity_date=day)
            registered += 1
        day += timedelta(days=1)


def test_streak_badge_awarded_and_progress_via_rules_engine(gamma_user_factory):
    # The real deploy path: seed the streak event types + the rule-driven badges of both kinds.
    call_command('initialize_continuous_learning_badges')
    user = _new_user(gamma_user_factory)

    _register_days(user.pk, 5)  # 5 consecutive active days (Mon-Fri)
    user.refresh_from_db()

    badge5 = Badge.objects.get(slug=DAILY_STREAK.badge_slug(5))
    badge10 = Badge.objects.get(slug=DAILY_STREAK.badge_slug(10))
    weekday_badge5 = Badge.objects.get(slug=WEEKDAY_STREAK.badge_slug(5))

    assert user.current_streak == 5
    # 5-day badge awarded by the rules engine.
    assert badge5.has_achievement(user) is True
    # Mon-Fri is also 5 consecutive weekdays, so that milestone lands at the same time.
    assert user.current_weekday_streak == 5
    assert weekday_badge5.has_achievement(user) is True
    # Bonuses (Badge.points=10 each) go to the total, NOT the Continuous Learning bucket;
    # the bucket holds only the daily points (5 days * 5).
    assert _bucket(user)['points'] == 5 * DAILY_ACTIVE_POINTS
    assert user.points == 5 * DAILY_ACTIVE_POINTS + 10 + 10
    # 10-day badge is in progress with the ring data reading current_streak (5/10).
    assert badge10.has_achievement(user) is True
    assert _streak_progress_count(user, badge10) == 5


def test_streak_badge_awarded_exactly_once(gamma_user_factory):
    call_command('initialize_continuous_learning_badges')
    user = _new_user(gamma_user_factory)

    _register_days(user.pk, 10)  # reach the 10-day milestone
    user.refresh_from_db()

    badge5 = Badge.objects.get(slug=DAILY_STREAK.badge_slug(5))
    badge10 = Badge.objects.get(slug=DAILY_STREAK.badge_slug(10))

    assert badge5.has_achievement(user) and badge10.has_achievement(user)
    assert _achievement_count(user, badge5) == 1  # not duplicated as the streak climbs past 5
    # Ten calendar days from a Monday span one weekend, so only 8 of them are weekdays:
    # the weekday run reaches 8 and stops short of its own 10-day milestone.
    assert user.current_weekday_streak == 8
    weekday_badge5 = Badge.objects.get(slug=WEEKDAY_STREAK.badge_slug(5))
    weekday_badge10 = Badge.objects.get(slug=WEEKDAY_STREAK.badge_slug(10))
    assert weekday_badge5.has_achievement(user) is True
    assert _streak_progress_count(user, weekday_badge10, WEEKDAY_STREAK) == 8
    # 10 daily*5 + 5-day(10) + 10-day(10) + 5-weekday(10); bucket holds only the daily points.
    assert user.points == 10 * DAILY_ACTIVE_POINTS + 10 + 10 + 10
    assert _bucket(user)['points'] == 10 * DAILY_ACTIVE_POINTS


def test_weekday_only_learner_earns_the_weekday_badges(gamma_user_factory):
    """
    The point of the feature: a learner who studies only Mon-Fri reaches the 10-weekday
    milestone, while their calendar-day run can never get past 5.
    """
    call_command('initialize_continuous_learning_badges')
    user = _new_user(gamma_user_factory)

    _register_weekdays(user.pk, 10)  # two full working weeks, no weekend activity
    user.refresh_from_db()

    weekday_badge10 = Badge.objects.get(slug=WEEKDAY_STREAK.badge_slug(10))
    day_badge10 = Badge.objects.get(slug=DAILY_STREAK.badge_slug(10))

    assert user.current_weekday_streak == 10
    assert weekday_badge10.has_achievement(user) is True
    # The calendar-day run reset every Monday and tops out at the working week.
    assert user.current_streak == 5
    assert day_badge10.has_achievement(user) is True   # in progress only...
    assert _streak_progress_count(user, day_badge10) == 5  # ...stuck at 5/10 forever


def test_initialize_command_seeds_both_kinds_and_is_idempotent():
    """The weekday badges mirror their day counterparts: same milestones, points and art."""
    call_command('initialize_continuous_learning_badges')
    call_command('initialize_continuous_learning_badges')  # re-running must not duplicate

    streak_badges = Badge.objects.filter(category='Continuous Learning')
    assert streak_badges.count() == 8  # 4 milestones x 2 kinds

    day10 = Badge.objects.get(slug='10-day-streak')
    weekday10 = Badge.objects.get(slug='10-weekday-streak')

    assert weekday10.title == '10 weekday streak'
    assert weekday10.description == (
        'You were active for 10 consecutive weekdays learning on the platform! Great job!'
    )
    assert day10.description == (
        'You were active for 10 consecutive days learning on the platform! Great job!'
    )
    # Same bonus and the same milestone artwork as the calendar-day badge.
    assert weekday10.points == day10.points
    assert weekday10.image and day10.image

    # Exactly one rule each, reading its own kind's counter — not duplicated by the re-run.
    assert weekday10.rules.count() == 1
    assert weekday10.rules.first().action == {WEEKDAY_STREAK.event_name: {'count': 10}}
    assert day10.rules.first().action == {DAILY_STREAK.event_name: {'count': 10}}


def test_weekday_badge_copies_the_day_badges_current_artwork():
    """
    A milestone's artwork is shared, and the day badges' images get replaced by hand in
    the badge editor — so the weekday badge must copy whatever its day counterpart is
    showing now, not the possibly-superseded PNG bundled in the repo.
    """
    call_command('initialize_continuous_learning_badges')

    replacement = b'REPLACEMENT-ARTWORK-NOT-THE-BUNDLED-FILE'
    day10 = Badge.objects.get(slug=DAILY_STREAK.badge_slug(10))
    day10.image.save('10-day-streak-v2.png', ContentFile(replacement), save=True)

    # Re-seed the weekday badge as a fresh environment would, after that replacement.
    Badge.objects.filter(slug=WEEKDAY_STREAK.badge_slug(10)).delete()
    call_command('initialize_continuous_learning_badges')

    weekday10 = Badge.objects.get(slug=WEEKDAY_STREAK.badge_slug(10))
    weekday10.image.open('rb')
    try:
        assert weekday10.image.read() == replacement
    finally:
        weekday10.image.close()


def test_reset_stale_streaks_zeros_broken_streak_and_ring(gamma_user_factory):
    call_command('initialize_continuous_learning_badges')
    user = _new_user(gamma_user_factory)
    _register_days(user.pk, 3)  # active DAY, DAY+1, DAY+2 (Mon-Wed) -> both runs at 3
    user.refresh_from_db()
    badge5 = Badge.objects.get(slug=DAILY_STREAK.badge_slug(5))
    assert user.current_streak == 3 and _streak_progress_count(user, badge5) == 3

    # Two days later (missed Thursday) -> both runs broken, so two counters reset.
    reset = reset_stale_streaks(today=DAY + timedelta(days=4))
    user.refresh_from_db()

    assert reset == 2
    assert user.current_streak == 0
    assert user.current_weekday_streak == 0
    assert _streak_progress_count(user, badge5) == 0  # ring dropped to 0%
    assert user.points == 3 * DAILY_ACTIVE_POINTS  # earned points are untouched


def test_reset_leaves_streak_active_yesterday_alone(gamma_user_factory):
    call_command('initialize_continuous_learning_badges')
    user = _new_user(gamma_user_factory)
    _register_days(user.pk, 3)  # last active = DAY+2 (Wednesday)

    # "Today" is the day right after the last active day: the streak is still continuable.
    reset = reset_stale_streaks(today=DAY + timedelta(days=3))
    user.refresh_from_db()

    assert reset == 0
    assert user.current_streak == 3  # preserved
    assert user.current_weekday_streak == 3


def test_reset_carries_the_weekday_streak_across_the_weekend(gamma_user_factory):
    """
    The daily job must not treat an idle Saturday/Sunday as a broken weekday run: the
    learner's next chance to extend it is Monday.
    """
    call_command('initialize_continuous_learning_badges')
    user = _new_user(gamma_user_factory)
    _register_days(user.pk, 5)  # Mon-Fri, both runs at 5

    # Saturday: nothing is due yet for either kind.
    assert reset_stale_streaks(today=SATURDAY) == 0

    # Sunday: the calendar-day run has now missed a full day and breaks; the weekday run
    # is still aimed at Monday and survives.
    assert reset_stale_streaks(today=SUNDAY) == 1
    user.refresh_from_db()
    assert user.current_streak == 0
    assert user.current_weekday_streak == 5

    # Monday, before the learner has done anything: still live and extendable.
    assert reset_stale_streaks(today=NEXT_MONDAY) == 0
    user.refresh_from_db()
    assert user.current_weekday_streak == 5


def test_reset_breaks_the_weekday_streak_after_a_missed_weekday(gamma_user_factory):
    call_command('initialize_continuous_learning_badges')
    user = _new_user(gamma_user_factory)
    _register_days(user.pk, 5)  # Mon-Fri, weekday run at 5
    weekday_badge5 = Badge.objects.get(slug=WEEKDAY_STREAK.badge_slug(5))
    weekday_badge10 = Badge.objects.get(slug=WEEKDAY_STREAK.badge_slug(10))

    # The learner skipped Monday; by Tuesday the weekday run is genuinely broken.
    reset_stale_streaks(today=NEXT_MONDAY + timedelta(days=1))
    user.refresh_from_db()

    assert user.current_weekday_streak == 0
    # The still-unearned milestone's ring drops back to 0%...
    assert _streak_progress_count(user, weekday_badge10, WEEKDAY_STREAK) == 0
    # ...while the badge already earned at 5 weekdays is kept, along with its points.
    assert weekday_badge5.has_achievement(user) is True
    assert user.points == 5 * DAILY_ACTIVE_POINTS + 10 + 10


def test_reset_is_noop_when_disabled(gamma_user_factory, settings):
    user = gamma_user_factory(
        points=0, chart={}, current_streak=3, last_active_date=DAY,
        current_weekday_streak=3, last_weekday_active_date=DAY,
    )
    settings.RGG_CONTINUOUS_LEARNING_ENABLED = False

    assert reset_stale_streaks(today=DAY + timedelta(days=4)) == 0
    user.refresh_from_db()
    assert user.current_streak == 3
    assert user.current_weekday_streak == 3


@pytest.mark.enable_signals
def test_common_event_through_signal_registers_active_day(
    gamma_user_factory, event_configuration_factory, event_factory,
):
    """End-to-end: a common point-earning Event fires the signal and credits an active day."""
    user = _new_user(gamma_user_factory)
    configuration = event_configuration_factory(event_type__name='edx_done_toggled', award=5)

    event_factory(configuration=configuration, username=user.user_uid)
    user.refresh_from_db()

    assert user.current_streak == 1
    # This one runs against the real "today", so the weekday run only starts on a weekday.
    assert user.current_weekday_streak == (1 if WEEKDAY_STREAK.counts(date.today()) else 0)
    assert _bucket(user)['points'] == DAILY_ACTIVE_POINTS
    # Event award (5) + daily Continuous Learning award (5).
    assert user.points == 5 + DAILY_ACTIVE_POINTS

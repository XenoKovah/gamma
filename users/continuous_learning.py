"""
Continuous Learning — daily activity points and consecutive-day streak badges.

A learner has an "active day" whenever they are logged in and perform an action that
earns them points (submitting an answer, completing a unit, posting in the forum, …).
Because earning points requires an authenticated session, "earned points today" already
implies "logged in today", so an active day is detected simply by a point-earning event
arriving for the user (see ``rules.signals.process_event_creation``).

For every active day the learner is awarded :data:`DAILY_ACTIVE_POINTS` into a single
"Continuous Learning" bucket on their Points Distribution. Consecutive active days build
a streak; reaching one of :data:`STREAK_MILESTONES` grants the matching "{N} day streak"
badge and its bonus points (also folded into the same bucket).

There is deliberately no EventType/EventConfiguration for these points: a configuration
carries one fixed ``award`` per type, but Continuous Learning mixes several amounts
(daily 5 plus 10/10/25/50 bonuses) that must all land in one bucket. The points are
therefore written straight to the user's totals/chart/progress via GammaUser helpers.

All work runs under the per-user row lock already held by the event signal, so the
read-modify-write of the streak counter and points is safe against concurrent events.
"""
from datetime import date, datetime, timedelta
from typing import Optional

from django.apps import apps
from django.conf import settings

# Single Points Distribution bucket that all Continuous Learning points accumulate into.
# The frontend chart is data-driven (bucket label = stored ``title``), so no UI change is
# needed for this bucket to appear.
CONTINUOUS_LEARNING_KEY = 'continuous_learning'
CONTINUOUS_LEARNING_TITLE = 'Continuous Learning'

# Free-text grouping label applied to the streak badges (Badge.category), used to group
# them together on the all-badges page.
CONTINUOUS_LEARNING_CATEGORY = 'Continuous Learning'

# Points awarded for each active day.
DAILY_ACTIVE_POINTS = 5

# Consecutive-active-day milestones, ascending: streak length -> bonus points granted by
# that milestone's "{N} day streak" badge. Keep ascending — the award loop relies on it.
STREAK_MILESTONES = (
    (5, 10),
    (10, 10),
    (20, 25),
    (30, 50),
)

# Events that credit points to a user *without that user being active that day* must not
# count toward an active day or a streak. ``edx_forum_thread_voted`` pays the post's
# author when someone *else* up-votes it, so the author may not have been present at all.
PASSIVE_EVENT_NAMES = frozenset({'edx_forum_thread_voted'})


def streak_badge_slug(days: int) -> str:
    """Stable slug used to look up / create a milestone badge (matches slugify of title)."""
    return f'{days}-day-streak'


def streak_badge_title(days: int) -> str:
    return f'{days} day streak'


def streak_badge_description(days: int) -> str:
    return f'You were active for {days} consecutive days learning on the platform! Great job!'


def is_enabled() -> bool:
    """Whether Continuous Learning processing is on (kill-switch, default on)."""
    return getattr(settings, 'RGG_CONTINUOUS_LEARNING_ENABLED', True)


def register_active_day(
    user,
    event_name: Optional[str] = None,
    activity_date: Optional[date] = None,
    force: bool = False,
) -> bool:
    """
    Record that ``user`` was active on ``activity_date`` (defaults to today) and, if this
    is the first qualifying activity of that day, award the daily points, advance the
    streak and grant any milestone badges now due.

    ``event_name`` is the triggering event's type; passive events (see
    :data:`PASSIVE_EVENT_NAMES`) never count. ``force`` bypasses the feature kill-switch
    (used by the backfill command, which is an explicit admin action). Returns ``True``
    when the day was newly counted, ``False`` when it was a no-op (feature off, passive
    event, or already counted today). Idempotent within a calendar day.
    """
    if not force and not is_enabled():
        return False

    if event_name in PASSIVE_EVENT_NAMES:
        return False

    if activity_date is None:
        # Mirror update_user_progress's notion of "today" (naive server-local now) so the
        # streak day and the points-timeline entry always agree.
        activity_date = datetime.now().date()

    if user.last_active_date == activity_date:
        # Already counted today — don't double-award the daily points.
        return False

    if user.last_active_date == activity_date - timedelta(days=1):
        user.current_streak += 1
    else:
        user.current_streak = 1
    user.last_active_date = activity_date
    user.save(update_fields=('current_streak', 'last_active_date'))

    _award_continuous_learning_points(user, DAILY_ACTIVE_POINTS, activity_date)
    _award_due_streak_badges(user, activity_date)
    return True


def _award_continuous_learning_points(user, amount: int, when: date) -> None:
    """Add ``amount`` to the user's total, daily progress (on ``when``) and the bucket."""
    user.update_user_points(amount)
    user.update_user_progress(amount, when=when)
    user.add_chart_points(CONTINUOUS_LEARNING_KEY, CONTINUOUS_LEARNING_TITLE, amount)


def _award_due_streak_badges(user, when: date) -> None:
    """
    Grant every milestone badge the user's current streak now satisfies but does not yet
    hold. Uses ``>=`` (not ``==``) so it self-heals if a milestone was missed earlier
    (e.g. badges seeded after the streak had already climbed). The bonus points are paid
    by ``Badge.award_to_user`` (into total + progress) and additionally folded into the
    Continuous Learning bucket so the bucket reflects all streak points.
    """
    Badge = apps.get_model('badges', 'Badge')

    for days, _bonus in STREAK_MILESTONES:
        if user.current_streak < days:
            # Ascending milestones: nothing higher can be due either.
            break

        badge = Badge.objects.filter(slug=streak_badge_slug(days), is_active=True).first()
        if badge is None or badge.has_achievement(user):
            continue

        newly_granted = badge.award_to_user(user)
        if newly_granted and badge.points:
            user.add_chart_points(CONTINUOUS_LEARNING_KEY, CONTINUOUS_LEARNING_TITLE, badge.points)

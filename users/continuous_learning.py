"""
Continuous Learning — daily activity points and consecutive-day streak badges.

A learner has an "active day" whenever they are logged in and perform an action that
earns them points (submitting an answer, completing a unit, posting in the forum, …).
Because earning points requires an authenticated session, "earned points today" already
implies "logged in today", so an active day is detected simply by a point-earning event
arriving for the user (see ``rules.signals.process_event_creation``).

For every active day the learner is awarded :data:`DAILY_ACTIVE_POINTS` into a single
"Continuous Learning" bucket on their Points Distribution. The daily points have no
EventConfiguration (one config carries a single fixed award, but the bucket needs to
accept the plain daily amount), so they are written straight to the user's
totals/chart/progress via GammaUser helpers.

Consecutive active days build a streak. The "{N} day streak" badges are ordinary
rule-driven badges (one rule each, action ``{rgg_continuous_learning_streak: {count: N}}``)
awarded by the rules engine — exactly like the points-threshold badges. After the streak
counter advances we emit the internal ``rgg_continuous_learning_streak`` event so those
rules re-evaluate against ``current_streak``: the dashboard then shows an in-progress ring
(current_streak / N) and the badge completes — paying its bonus points to the user's total
and points timeline via the normal completion path — when the streak reaches N.

All work runs under the per-user row lock already held by the event signal, so the
read-modify-write of the streak counter and points is safe against concurrent events.
"""
from datetime import date, datetime, timedelta
from typing import Optional

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

# Consecutive-active-day milestones: streak length -> bonus points configured as the
# matching "{N} day streak" badge's completion points (Badge.points), paid by the rules
# engine when the badge completes. Used by initialize_continuous_learning_badges to seed
# the badges and their rules.
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
    _trigger_streak_badge_evaluation(user)
    return True


def _award_continuous_learning_points(user, amount: int, when: date) -> None:
    """Add ``amount`` to the user's total, daily progress (on ``when``) and the bucket."""
    user.update_user_points(amount)
    user.update_user_progress(amount, when=when)
    user.add_chart_points(CONTINUOUS_LEARNING_KEY, CONTINUOUS_LEARNING_TITLE, amount)


def _trigger_streak_badge_evaluation(user) -> None:
    """
    Re-evaluate the streak badges against the user's just-updated ``current_streak``.

    Emits the internal ``rgg_continuous_learning_streak`` event so the rules engine
    updates each streak badge's progress (current_streak / N) and awards it on reaching N
    — the same mechanism the points-threshold badges use. Guarded: if the streak event
    type has not been seeded yet (initialize_continuous_learning_badges), this is a no-op
    rather than raising and breaking event processing for everyone.
    """
    from events.enums import RggInternalEventTypes
    from events.models import EventConfiguration
    from events.utils import simulate_rgg_internal_event

    event_name = RggInternalEventTypes.RGG_CONTINUOUS_LEARNING_STREAK.value
    if EventConfiguration.objects.filter(event_type__name=event_name).exists():
        simulate_rgg_internal_event(user, event_name)

"""
Tests for ``backfill_badge_completion_points`` — the retroactive payout for learners who
earned a badge while it was still worth zero.
"""
from datetime import timedelta

import pytest
from django.contrib.contenttypes.models import ContentType
from django.core.management import CommandError, call_command
from django.utils.timezone import now

from achievements.models import Achievement
from badges.models import Badge

pytestmark = pytest.mark.django_db

CUTOFF = '2026-07-20T00:00:00Z'
BEFORE_CUTOFF = now().replace(year=2026, month=7, day=1)
AFTER_CUTOFF = now().replace(year=2026, month=7, day=25)


@pytest.fixture
def triangle(badge_factory) -> Badge:
    """A 'triangle' badge: earned by many learners while it was worth nothing."""
    return badge_factory(title='Set Country', points=0)


def earn(badge, user, when=BEFORE_CUTOFF, paid=None):
    """Give ``user`` a completed achievement for ``badge``, as the live pipeline would."""
    return Achievement.objects.create(
        user=user,
        content_type=ContentType.objects.get_for_model(Badge),
        object_id=badge.pk,
        title=badge.title,
        completed_at=when,
        completion_points_paid=paid,
    )


def run(**kwargs):
    options = {'completed_before': CUTOFF, 'commit': True}
    options.update(kwargs)
    call_command('backfill_badge_completion_points', **options)


def test_pays_existing_holders_and_sets_the_new_value(triangle, gamma_user_factory):
    user = gamma_user_factory(points=100)
    achievement = earn(triangle, user)

    run(points_map=f'{triangle.pk}=50')

    triangle.refresh_from_db()
    user.refresh_from_db()
    achievement.refresh_from_db()
    assert triangle.points == 50
    assert user.points == 150
    assert achievement.completion_points_paid == 50


def test_is_idempotent(triangle, gamma_user_factory):
    user = gamma_user_factory(points=100)
    earn(triangle, user)

    run(points_map=f'{triangle.pk}=50')
    run(points_map=f'{triangle.pk}=50')
    run(badge_ids=str(triangle.pk))

    user.refresh_from_db()
    assert user.points == 150, 'a re-run must not pay a second time'


def test_dry_run_changes_nothing(triangle, gamma_user_factory):
    user = gamma_user_factory(points=100)
    achievement = earn(triangle, user)

    run(points_map=f'{triangle.pk}=50', commit=False)

    triangle.refresh_from_db()
    user.refresh_from_db()
    achievement.refresh_from_db()
    assert (triangle.points, user.points, achievement.completion_points_paid) == (0, 100, None)


def test_skips_achievements_completed_after_the_cutoff(triangle, gamma_user_factory):
    """Earned once the badge already had a value, so the live path already paid it."""
    user = gamma_user_factory(points=100)
    earn(triangle, user, when=AFTER_CUTOFF)

    run(points_map=f'{triangle.pk}=50')

    user.refresh_from_db()
    assert user.points == 100


def test_skips_achievements_already_paid(triangle, gamma_user_factory):
    user = gamma_user_factory(points=100)
    earn(triangle, user, paid=50)

    run(points_map=f'{triangle.pk}=50')

    user.refresh_from_db()
    assert user.points == 100


def test_pays_each_of_a_learners_badges(badge_factory, gamma_user_factory):
    """The screenshot case: one learner holding several triangles gets paid for each."""
    photo = badge_factory(title='Set Photo', points=0)
    enrolled = badge_factory(title='Enrolled in a Course', points=0)
    user = gamma_user_factory(points=100)
    earn(photo, user)
    earn(enrolled, user)

    run(points_map=f'{photo.pk}=50,{enrolled.pk}=25')

    user.refresh_from_db()
    assert user.points == 175


def test_credits_the_timeline_to_the_day_the_badge_was_earned(triangle, gamma_user_factory):
    user = gamma_user_factory(points=0, progress={})
    earn(triangle, user)

    run(points_map=f'{triangle.pk}=50')

    user.refresh_from_db()
    entries = user.progress['2026']
    assert len(entries) == 1
    assert entries[0]['date'].startswith('2026-07-01')
    assert entries[0]['points'] == 50


def test_timeline_today_credits_the_current_day_instead(triangle, gamma_user_factory):
    user = gamma_user_factory(points=0, progress={})
    earn(triangle, user)

    run(points_map=f'{triangle.pk}=50', timeline='today')

    user.refresh_from_db()
    entries = user.progress[str(now().year)]
    assert entries[0]['date'].startswith(now().strftime('%Y-%m-%d'))


def test_limit_and_user_uid_scope_the_run(triangle, gamma_user_factory):
    first = gamma_user_factory(points=0, user_uid='first')
    second = gamma_user_factory(points=0, user_uid='second')
    earn(triangle, first)
    earn(triangle, second)

    run(points_map=f'{triangle.pk}=50', user_uid='second')

    first.refresh_from_db()
    second.refresh_from_db()
    assert (first.points, second.points) == (0, 50)


def test_badges_mode_uses_the_current_value_without_changing_it(badge_factory, gamma_user_factory):
    badge = badge_factory(title='Set Bio', points=30)
    user = gamma_user_factory(points=0)
    earn(badge, user)

    run(badge_ids=str(badge.pk))

    badge.refresh_from_db()
    user.refresh_from_db()
    assert (badge.points, user.points) == (30, 30)


def test_zero_point_badge_is_recorded_as_paid_not_skipped(triangle, gamma_user_factory):
    """Stamping 0 stops a later real backfill from silently re-considering the row."""
    user = gamma_user_factory(points=100)
    achievement = earn(triangle, user)

    run(points_map=f'{triangle.pk}=0')

    user.refresh_from_db()
    achievement.refresh_from_db()
    assert user.points == 100
    assert achievement.completion_points_paid == 0


def test_negative_points_badge_docks(badge_factory, gamma_user_factory):
    penalty = badge_factory(title='Speed-runner!', points=0)
    user = gamma_user_factory(points=100)
    earn(penalty, user)

    run(points_map=f'{penalty.pk}=-50')

    user.refresh_from_db()
    assert user.points == 50


def test_in_progress_achievements_are_not_paid(triangle, gamma_user_factory):
    user = gamma_user_factory(points=100)
    earn(triangle, user, when=None)

    run(points_map=f'{triangle.pk}=50')

    user.refresh_from_db()
    assert user.points == 100


@pytest.mark.parametrize('kwargs, message', [
    ({'points_map': '10=50'}, 'No badge with id'),
    ({'badge_ids': '10'}, 'No badge with id'),
    ({'points_map': 'nonsense'}, 'BADGE_ID=POINTS form'),
    ({'points_map': 'x=y'}, 'non-integer'),
])
def test_rejects_bad_scope(kwargs, message):
    with pytest.raises(CommandError, match=message):
        run(**kwargs)


def test_rejects_an_unparseable_cutoff(triangle):
    with pytest.raises(CommandError, match='ISO-8601'):
        run(points_map=f'{triangle.pk}=50', completed_before='last tuesday')


def test_revoke_reverses_exactly_what_was_paid(triangle, gamma_user_factory):
    """Re-valuing a badge after the backfill must not change what a revoke claws back."""
    user = gamma_user_factory(points=100)
    earn(triangle, user)
    run(points_map=f'{triangle.pk}=50')
    # revoke_from_user subtracts from the passed-in instance's in-memory total, so it must
    # be given a fresh one — this instance still reads 100, from before the backfill.
    user.refresh_from_db()

    triangle.refresh_from_db()
    triangle.points = 500
    triangle.save(update_fields=('points',))
    triangle.revoke_from_user(user)

    user.refresh_from_db()
    assert user.points == 100, 'revoke must reverse the 50 actually paid, not the new 500'


def test_completion_use_case_records_what_it_paid(badge_factory, gamma_user_factory):
    """The live path stamps the field too, so future backfills can trust it."""
    from achievements.usecases import AchievementCompletionUseCase

    badge = badge_factory(title='Instructor', points=100)
    user = gamma_user_factory(points=0)
    achievement = earn(badge, user, when=None)

    AchievementCompletionUseCase().execute(achievement)

    achievement.refresh_from_db()
    user.refresh_from_db()
    assert achievement.completion_points_paid == 100
    assert user.points == 100


def test_manual_grant_records_what_it_paid(badge_factory, gamma_user_factory):
    badge = badge_factory(title='Instructor', points=100_000)
    user = gamma_user_factory(points=0)

    badge.award_to_user(user)

    achievement = Achievement.objects.get(user=user, object_id=badge.pk)
    assert achievement.completion_points_paid == 100_000


def test_backfill_ignores_a_badge_whose_holders_were_already_paid(badge_factory, gamma_user_factory):
    """Course Completion badges pay at grant time; sweeping them in would double-credit."""
    course_badge = badge_factory(title='Architecture 1001', points=28_500)
    user = gamma_user_factory(points=0)
    course_badge.award_to_user(user)

    run(badge_ids=str(course_badge.pk))

    user.refresh_from_db()
    assert user.points == 28_500

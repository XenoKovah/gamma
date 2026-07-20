"""
Tests for ``Badge.excluded_categories`` — the guard that refuses to grant a badge to a
learner who already holds a badge in a disqualifying category (e.g. the "Ignominious!"
anti-gaming badges blocking the "Completionist" accomplishment).
"""
import pytest

from achievements.models import Achievement
from badges.exceptions import BadgeExclusionError
from badges.models import Badge

pytestmark = pytest.mark.django_db

IGNOMINIOUS = 'Ignominious!'


@pytest.fixture
def prize(badge_factory) -> Badge:
    """A badge that cannot be earned by anyone holding an 'Ignominious!' badge."""
    return badge_factory(
        title='Completionist',
        category='Manually-assigned Uber-accomplishments',
        points=1_000_000,
        excluded_categories=[IGNOMINIOUS],
    )


@pytest.fixture
def penalty(badge_factory) -> Badge:
    return badge_factory(title='Speed-runner!', category=IGNOMINIOUS, points=-50)


def test_defaults_to_no_exclusions(badge_factory, gamma_user_factory):
    """Existing badges are unaffected: no exclusions configured means nothing is blocked."""
    badge = badge_factory(title='Instructor', points=100)
    user = gamma_user_factory()

    assert badge.excluded_categories == []
    assert not badge.blocking_badges(user).exists()
    assert badge.award_to_user(user) is True


def test_award_blocked_when_user_holds_excluded_badge(prize, penalty, gamma_user_factory):
    user = gamma_user_factory()
    penalty.award_to_user(user)
    points_before = user.points

    with pytest.raises(BadgeExclusionError) as exc_info:
        prize.award_to_user(user)

    assert list(exc_info.value.blocking_badges) == [penalty]
    assert 'Speed-runner!' in str(exc_info.value)
    # The grant is refused outright: no achievement, and no points paid out.
    assert not prize.has_achievement(user)
    user.refresh_from_db()
    assert user.points == points_before


def test_award_allowed_when_user_holds_no_excluded_badge(prize, penalty, gamma_user_factory):
    """Holding an unrelated badge in a non-excluded category must not block the grant."""
    user = gamma_user_factory()

    assert prize.award_to_user(user) is True
    assert prize.has_achievement(user)


def test_unrelated_category_does_not_block(prize, badge_factory, gamma_user_factory):
    user = gamma_user_factory()
    badge_factory(title='Subtitle Superhero', category='Valiant Volunteerism!').award_to_user(user)

    assert prize.award_to_user(user) is True


def test_already_held_badge_stays_idempotent_after_user_is_flagged(prize, penalty, gamma_user_factory):
    """
    A learner who earned the badge *before* being flagged keeps it, and re-assigning
    stays a no-op rather than starting to raise.
    """
    user = gamma_user_factory()
    assert prize.award_to_user(user) is True

    penalty.award_to_user(user)

    assert prize.award_to_user(user) is False
    assert prize.has_achievement(user)


def test_blocking_badges_reports_every_disqualifier(prize, penalty, badge_factory, gamma_user_factory):
    user = gamma_user_factory()
    other_penalty = badge_factory(title='Watchlister', category=IGNOMINIOUS, points=-50)
    penalty.award_to_user(user)
    other_penalty.award_to_user(user)

    assert set(prize.blocking_badges(user)) == {penalty, other_penalty}


def test_exclusion_is_per_user(prize, penalty, gamma_user_factory):
    """One flagged learner must not block the badge for everyone else."""
    flagged, clean = gamma_user_factory(), gamma_user_factory()
    penalty.award_to_user(flagged)

    with pytest.raises(BadgeExclusionError):
        prize.award_to_user(flagged)
    assert prize.award_to_user(clean) is True


def test_revoke_is_not_blocked(prize, penalty, gamma_user_factory):
    """Exclusions gate granting only — removing a badge must always be possible."""
    user = gamma_user_factory()
    prize.award_to_user(user)
    penalty.award_to_user(user)

    assert prize.revoke_from_user(user) is True
    assert not prize.has_achievement(user)


def test_bulk_assign_reports_blocked_without_stranding_others(
    prize, penalty, gamma_user_factory, client, user_factory,
):
    """A blocked user in a bulk assign must not stop the eligible ones being granted."""
    flagged, clean = gamma_user_factory(), gamma_user_factory()
    penalty.award_to_user(flagged)
    client.force_login(user_factory(is_staff=True))

    response = client.post(
        f'/api/v0/badges/{prize.id}/assign/',
        {'user_uids': [flagged.user_uid, clean.user_uid]},
        format='json',
    )

    assert response.status_code == 200
    assert response.data['granted'] == [clean.user_uid]
    assert [b['user_uid'] for b in response.data['blocked']] == [flagged.user_uid]
    assert 'Speed-runner!' in response.data['blocked'][0]['reason']
    assert Achievement.objects.filter(object_id=prize.id).count() == 1

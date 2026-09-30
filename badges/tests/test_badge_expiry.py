"""
Tests for time-limited badge grants (``Achievement.expires_at`` / ``Badge.validity_days``).
"""
from datetime import timedelta

import pytest
from django.contrib.contenttypes.models import ContentType
from django.utils.timezone import now

from achievements.models import Achievement
from achievements.usecases import PendingBadgeNotificationsUseCase
from badges.models import Badge
from badges.utils import is_achieved_badge

pytestmark = pytest.mark.django_db


def _grant(badge, user):
    return Achievement.objects.get(
        user=user, content_type=ContentType.objects.get_for_model(Badge), object_id=badge.id,
    )


def test_grant_without_expiry_never_lapses(badge_factory, gamma_user_factory):
    badge, user = badge_factory(title='Forever', points=10), gamma_user_factory()

    assert badge.award_to_user(user) is True

    grant = _grant(badge, user)
    assert grant.expires_at is None
    assert not grant.is_expired
    assert Achievement.objects.unexpired().filter(pk=grant.pk).exists()


def test_explicit_expires_at_is_stored(badge_factory, gamma_user_factory):
    badge, user = badge_factory(title='Five years', points=10), gamma_user_factory()
    lapse = now() + timedelta(days=5 * 365)

    badge.award_to_user(user, expires_at=lapse)

    assert _grant(badge, user).expires_at == lapse


def test_validity_days_sets_default_expiry(badge_factory, gamma_user_factory):
    badge, user = badge_factory(title='Yearly', points=10, validity_days=365), gamma_user_factory()

    badge.award_to_user(user)

    delta = _grant(badge, user).expires_at - now()
    assert timedelta(days=364) < delta <= timedelta(days=365)


def test_explicit_expiry_overrides_validity_days(badge_factory, gamma_user_factory):
    badge, user = badge_factory(title='Yearly', points=10, validity_days=365), gamma_user_factory()
    lapse = now() + timedelta(days=5 * 365)

    badge.award_to_user(user, expires_at=lapse)

    assert _grant(badge, user).expires_at == lapse


def test_past_expiry_is_expired_and_excluded(badge_factory, gamma_user_factory):
    badge, user = badge_factory(title='Lapsed', points=10), gamma_user_factory()
    badge.award_to_user(user, expires_at=now() - timedelta(seconds=1))

    grant = _grant(badge, user)
    assert grant.is_expired
    assert not Achievement.objects.unexpired().filter(pk=grant.pk).exists()
    assert not is_achieved_badge(grant, None)


def test_lapsed_grant_does_not_notify(badge_factory, gamma_user_factory):
    badge, user = badge_factory(title='Lapsed', points=10), gamma_user_factory()
    badge.award_to_user(user, expires_at=now() - timedelta(seconds=1))

    assert PendingBadgeNotificationsUseCase().execute(user.user_uid) == []


def test_renewal_extends_expiry_without_repaying_points(badge_factory, gamma_user_factory):
    badge, user = badge_factory(title='Donor', points=100), gamma_user_factory()
    badge.award_to_user(user, expires_at=now() - timedelta(days=1))
    user.refresh_from_db()
    points_after_first = user.points
    renewed = now() + timedelta(days=365)

    assert badge.award_to_user(user, expires_at=renewed) is False

    user.refresh_from_db()
    assert user.points == points_after_first
    grant = _grant(badge, user)
    assert grant.expires_at == renewed
    assert not grant.is_expired


def test_repeat_award_with_no_expiry_leaves_live_grant_alone(badge_factory, gamma_user_factory):
    badge, user = badge_factory(title='Donor', points=100), gamma_user_factory()
    lapse = now() + timedelta(days=30)
    badge.award_to_user(user, expires_at=lapse)

    assert badge.award_to_user(user) is False

    assert _grant(badge, user).expires_at == lapse


def test_lapsed_grant_renews_by_validity_days(badge_factory, gamma_user_factory):
    badge, user = badge_factory(title='Yearly', points=10, validity_days=365), gamma_user_factory()
    badge.award_to_user(user, expires_at=now() - timedelta(days=1))

    assert badge.award_to_user(user) is False

    assert not _grant(badge, user).is_expired


def test_lapsed_badge_does_not_block_exclusions(badge_factory, gamma_user_factory):
    penalty = badge_factory(title='Speed-runner!', category='Ignominious!', points=-50)
    prize = badge_factory(title='Completionist', points=10, excluded_categories=['Ignominious!'])
    user = gamma_user_factory()
    penalty.award_to_user(user, expires_at=now() - timedelta(days=1))

    assert not prize.blocking_badges(user).exists()
    assert prize.award_to_user(user) is True

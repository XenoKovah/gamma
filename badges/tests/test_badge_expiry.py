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


class TestExpiryApi:
    """Admin endpoints for per-user expiry on an expiring badge."""

    @staticmethod
    def _url(name, badge):
        from django.urls import reverse
        return reverse(f'badges:api:v0:badge-{name}', kwargs={'pk': badge.id})

    @staticmethod
    def _admin(client, user_factory):
        client.force_authenticate(user=user_factory(is_staff=True))
        return client

    def test_endpoints_require_admin(self, client, badge_factory):
        badge = badge_factory(is_expiring=True)
        assert client.get(self._url('holders', badge)).status_code in (401, 403)
        assert client.post(self._url('expire', badge), {'user_uids': ['x']}, format='json').status_code in (401, 403)
        assert client.post(self._url('set-expiry', badge), {'user_uids': ['x'], 'expires_at': None},
                           format='json').status_code in (401, 403)

    def test_non_expiring_badge_rejects_expiry_operations(self, client, badge_factory, user_factory):
        badge = badge_factory(is_expiring=False)
        admin = self._admin(client, user_factory)

        assert admin.get(self._url('holders', badge)).status_code == 400
        assert admin.post(self._url('expire', badge), {'user_uids': ['x']}, format='json').status_code == 400
        assert admin.post(
            self._url('assign', badge), {'user_uids': ['x'], 'expires_at': '2031-01-01T00:00:00Z'}, format='json',
        ).status_code == 400

    def test_assign_with_per_user_expiry(self, client, badge_factory, gamma_user_factory, user_factory):
        badge = badge_factory(is_expiring=True, points=50)
        five, ten = gamma_user_factory(), gamma_user_factory()
        admin = self._admin(client, user_factory)

        for user, when in ((five, '2031-09-29T23:59:59Z'), (ten, '2036-09-29T23:59:59Z')):
            response = admin.post(
                self._url('assign', badge), {'user_uids': [user.user_uid], 'expires_at': when}, format='json',
            )
            assert response.status_code == 200
            assert response.json()['granted'] == [user.user_uid]

        assert _grant(badge, five).expires_at.year == 2031
        assert _grant(badge, ten).expires_at.year == 2036

    def test_holders_lists_expiry_soonest_first(self, client, badge_factory, gamma_user_factory, user_factory):
        badge = badge_factory(is_expiring=True)
        soon, later, never = gamma_user_factory(), gamma_user_factory(), gamma_user_factory()
        badge.award_to_user(never)
        badge.award_to_user(later, expires_at=now() + timedelta(days=400))
        badge.award_to_user(soon, expires_at=now() + timedelta(days=10))

        data = self._admin(client, user_factory).get(self._url('holders', badge)).json()['holders']

        assert [h['user_uid'] for h in data] == [soon.user_uid, later.user_uid, never.user_uid]
        assert data[2]['expires_at'] is None and data[0]['is_expired'] is False

    def test_expire_now_then_restore(self, client, badge_factory, gamma_user_factory, user_factory):
        badge = badge_factory(is_expiring=True, points=100)
        user = gamma_user_factory()
        badge.award_to_user(user, expires_at=now() + timedelta(days=365))
        user.refresh_from_db()
        points = user.points
        admin = self._admin(client, user_factory)

        response = admin.post(self._url('expire', badge), {'user_uids': [user.user_uid]}, format='json')
        assert response.status_code == 200 and response.json()['updated'] == [user.user_uid]
        assert _grant(badge, user).is_expired

        restored = admin.post(
            self._url('set-expiry', badge),
            {'user_uids': [user.user_uid], 'expires_at': '2040-01-01T00:00:00Z'}, format='json',
        )
        assert restored.status_code == 200
        assert not _grant(badge, user).is_expired
        user.refresh_from_db()
        assert user.points == points

    def test_set_expiry_null_makes_permanent_and_skips_non_holders(
        self, client, badge_factory, gamma_user_factory, user_factory,
    ):
        badge = badge_factory(is_expiring=True)
        holder, stranger = gamma_user_factory(), gamma_user_factory()
        badge.award_to_user(holder, expires_at=now() + timedelta(days=5))

        response = self._admin(client, user_factory).post(
            self._url('set-expiry', badge),
            {'user_uids': [holder.user_uid, stranger.user_uid], 'expires_at': None}, format='json',
        )

        assert response.json()['updated'] == [holder.user_uid]
        assert response.json()['not_assigned'] == [stranger.user_uid]
        assert _grant(badge, holder).expires_at is None
        assert not badge.has_achievement(stranger)

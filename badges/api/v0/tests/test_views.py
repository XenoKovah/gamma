import pytest
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse_lazy
from rest_framework import status

from achievements.models import Achievement
from badges.models import Badge
from users.models import GammaUser


pytestmark = pytest.mark.django_db


class TestBadgeViewSet:

    def test_get_badge_list(self, client, badge_factory):
        badge_factory.create_batch(3)
        response = client.get(reverse_lazy('badges:api:v0:badge-list'))

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 3

    def test_get_badge_detail(self, client, badge_factory):
        badge = badge_factory()
        url = reverse_lazy('badges:api:v0:badge-detail', kwargs={'pk': badge.id})
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            'id': badge.id,
            'title': badge.title,
            'description': badge.description,
            'category': badge.category,
            'image': f'http://testserver/media/{badge.image}',
            'slug': badge.slug,
            'is_active': badge.is_active,
            'points': badge.points,
            'manual_criteria': badge.manual_criteria,
            'rules': [],
            'created_at': badge.created_at.isoformat().replace('+00:00', 'Z'),
        }


class TestBadgeAssign:

    @staticmethod
    def _assign_url(badge):
        return reverse_lazy('badges:api:v0:badge-assign', kwargs={'pk': badge.id})

    @staticmethod
    def _admin_client(client, user_factory):
        client.force_authenticate(user=user_factory(is_staff=True))
        return client

    def test_assign_requires_admin(self, client, badge_factory):
        badge = badge_factory()
        response = client.post(self._assign_url(badge), {'user_uids': ['someone']}, format='json')

        assert response.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)
        assert not Achievement.objects.exists()

    def test_assign_grants_badge_and_awards_points(self, client, badge_factory, gamma_user_factory, user_factory):
        badge = badge_factory(points=100)
        gamma_user = gamma_user_factory(points=100)
        admin_client = self._admin_client(client, user_factory)

        response = admin_client.post(
            self._assign_url(badge), {'user_uids': [gamma_user.user_uid]}, format='json',
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            'granted': [gamma_user.user_uid],
            'already_assigned': [],
            'points_each': 100,
        }

        content_type = ContentType.objects.get_for_model(Badge)
        achievement = Achievement.objects.get(
            user=gamma_user, content_type=content_type, object_id=badge.id,
        )
        # A manually granted badge has no rules, so it reads as completed/earned.
        assert achievement.all_rules_completed is True

        gamma_user.refresh_from_db()
        assert gamma_user.points == 200  # 100 starting + 100 from the badge

    def test_assign_creates_gamma_user_when_missing(self, client, badge_factory, user_factory):
        badge = badge_factory(points=50)
        admin_client = self._admin_client(client, user_factory)

        response = admin_client.post(
            self._assign_url(badge), {'user_uids': ['brand-new-uid']}, format='json',
        )

        assert response.status_code == status.HTTP_200_OK
        gamma_user = GammaUser.objects.get(user_uid='brand-new-uid')
        assert gamma_user.points == 50

    def test_assign_is_idempotent_and_does_not_double_award_points(
        self, client, badge_factory, gamma_user_factory, user_factory,
    ):
        badge = badge_factory(points=100)
        gamma_user = gamma_user_factory(points=0)
        admin_client = self._admin_client(client, user_factory)

        first = admin_client.post(
            self._assign_url(badge), {'user_uids': [gamma_user.user_uid]}, format='json',
        )
        second = admin_client.post(
            self._assign_url(badge), {'user_uids': [gamma_user.user_uid]}, format='json',
        )

        assert first.json()['granted'] == [gamma_user.user_uid]
        assert second.json()['granted'] == []
        assert second.json()['already_assigned'] == [gamma_user.user_uid]

        assert Achievement.objects.filter(object_id=badge.id, user=gamma_user).count() == 1
        gamma_user.refresh_from_db()
        assert gamma_user.points == 100  # awarded once, not twice

    def test_assign_deduplicates_user_uids(self, client, badge_factory, gamma_user_factory, user_factory):
        badge = badge_factory(points=10)
        gamma_user = gamma_user_factory(points=0)
        admin_client = self._admin_client(client, user_factory)

        response = admin_client.post(
            self._assign_url(badge),
            {'user_uids': [gamma_user.user_uid, gamma_user.user_uid]},
            format='json',
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()['granted'] == [gamma_user.user_uid]
        gamma_user.refresh_from_db()
        assert gamma_user.points == 10

    def test_assign_rejects_empty_user_uids(self, client, badge_factory, user_factory):
        badge = badge_factory()
        admin_client = self._admin_client(client, user_factory)

        response = admin_client.post(self._assign_url(badge), {'user_uids': []}, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_assign_without_points_grants_badge_only(self, client, badge_factory, gamma_user_factory, user_factory):
        badge = badge_factory(points=0)
        gamma_user = gamma_user_factory(points=42)
        admin_client = self._admin_client(client, user_factory)

        response = admin_client.post(
            self._assign_url(badge), {'user_uids': [gamma_user.user_uid]}, format='json',
        )

        assert response.status_code == status.HTTP_200_OK
        assert Achievement.objects.filter(object_id=badge.id, user=gamma_user).exists()
        gamma_user.refresh_from_db()
        assert gamma_user.points == 42  # unchanged


class TestBadgeUnassign:

    @staticmethod
    def _assign_url(badge):
        return reverse_lazy('badges:api:v0:badge-assign', kwargs={'pk': badge.id})

    @staticmethod
    def _unassign_url(badge):
        return reverse_lazy('badges:api:v0:badge-unassign', kwargs={'pk': badge.id})

    @staticmethod
    def _admin_client(client, user_factory):
        client.force_authenticate(user=user_factory(is_staff=True))
        return client

    def test_unassign_requires_admin(self, client, badge_factory, gamma_user_factory):
        badge = badge_factory()
        gamma_user = gamma_user_factory()
        response = client.post(self._unassign_url(badge), {'user_uids': [gamma_user.user_uid]}, format='json')

        assert response.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)

    def test_unassign_removes_badge_and_deducts_points(
        self, client, badge_factory, gamma_user_factory, user_factory,
    ):
        badge = badge_factory(points=100)
        gamma_user = gamma_user_factory(points=250)
        admin_client = self._admin_client(client, user_factory)
        # First grant it (250 -> 350), then remove it (350 -> 250).
        admin_client.post(self._assign_url(badge), {'user_uids': [gamma_user.user_uid]}, format='json')

        response = admin_client.post(
            self._unassign_url(badge), {'user_uids': [gamma_user.user_uid]}, format='json',
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            'removed': [gamma_user.user_uid],
            'not_assigned': [],
            'points_each': 100,
        }
        assert not Achievement.objects.filter(object_id=badge.id, user=gamma_user).exists()
        gamma_user.refresh_from_db()
        assert gamma_user.points == 250

    def test_unassign_floors_points_at_zero(self, client, badge_factory, gamma_user_factory, user_factory):
        badge = badge_factory(points=100)
        gamma_user = gamma_user_factory(points=30)  # fewer points than the badge is worth
        badge.award_to_user(gamma_user)  # 30 -> 130
        admin_client = self._admin_client(client, user_factory)

        admin_client.post(self._unassign_url(badge), {'user_uids': [gamma_user.user_uid]}, format='json')

        gamma_user.refresh_from_db()
        assert gamma_user.points == 30  # 130 - 100, not negative

    def test_unassign_noop_for_user_without_badge(
        self, client, badge_factory, gamma_user_factory, user_factory,
    ):
        badge = badge_factory(points=100)
        gamma_user = gamma_user_factory(points=42)
        admin_client = self._admin_client(client, user_factory)

        response = admin_client.post(
            self._unassign_url(badge), {'user_uids': [gamma_user.user_uid]}, format='json',
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()['removed'] == []
        assert response.json()['not_assigned'] == [gamma_user.user_uid]
        gamma_user.refresh_from_db()
        assert gamma_user.points == 42  # untouched

    def test_unassign_is_idempotent(self, client, badge_factory, gamma_user_factory, user_factory):
        badge = badge_factory(points=100)
        gamma_user = gamma_user_factory(points=0)
        admin_client = self._admin_client(client, user_factory)
        admin_client.post(self._assign_url(badge), {'user_uids': [gamma_user.user_uid]}, format='json')

        first = admin_client.post(self._unassign_url(badge), {'user_uids': [gamma_user.user_uid]}, format='json')
        second = admin_client.post(self._unassign_url(badge), {'user_uids': [gamma_user.user_uid]}, format='json')

        assert first.json()['removed'] == [gamma_user.user_uid]
        assert second.json()['removed'] == []
        assert second.json()['not_assigned'] == [gamma_user.user_uid]
        gamma_user.refresh_from_db()
        assert gamma_user.points == 0  # deducted once, floored, not below zero

from datetime import timedelta

import pytest
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.utils.timezone import now
from rest_framework import status

from avatars.models import Avatar
from badges.models import Badge
from users.models import GammaUser


@pytest.fixture
def badge_achievement(achievement_factory, badge_factory, gamma_user_factory):
    """
    A completed, not-yet-seen badge achievement (a pending notification).
    """
    badge = badge_factory()
    user = gamma_user_factory(user_uid='notified_user')
    return achievement_factory(
        user=user,
        content_type=ContentType.objects.get_for_model(Badge),
        object_id=badge.id,
        title='Snapshot title',
        completed_at=now(),
    )


@pytest.mark.django_db
def test_pending_badge_notifications_listed(auth_client, badge_achievement):
    url = reverse('users:api:v0:user-badge-notifications')

    response = auth_client.get(url, {'username': 'notified_user'})
    response_data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(response_data) == 1
    notification = response_data[0]
    assert set(notification.keys()) == {'uuid', 'slug', 'title', 'description', 'image', 'completed_at'}
    assert notification['uuid'] == str(badge_achievement.uuid)
    badge = badge_achievement.content_object
    assert notification['slug'] == badge.slug
    assert notification['title'] == badge.title
    assert notification['image'] == badge.image.url


@pytest.mark.django_db
def test_pending_badge_notifications_ordered_oldest_first(
    auth_client, achievement_factory, badge_factory, gamma_user_factory
):
    user = gamma_user_factory(user_uid='ordered_user')
    badge_content_type = ContentType.objects.get_for_model(Badge)
    newer = achievement_factory(
        user=user, content_type=badge_content_type, object_id=badge_factory().id, completed_at=now(),
    )
    older = achievement_factory(
        user=user,
        content_type=badge_content_type,
        object_id=badge_factory().id,
        completed_at=now() - timedelta(hours=1),
    )

    response = auth_client.get(reverse('users:api:v0:user-badge-notifications'), {'username': 'ordered_user'})

    uuids = [notification['uuid'] for notification in response.json()]
    assert uuids == [str(older.uuid), str(newer.uuid)]


@pytest.mark.django_db
def test_pending_badge_notifications_excludes_seen_incomplete_and_other_users(
    auth_client, achievement_factory, badge_factory, gamma_user_factory, badge_achievement
):
    badge_content_type = ContentType.objects.get_for_model(Badge)
    user = badge_achievement.user
    # Already seen.
    achievement_factory(
        user=user,
        content_type=badge_content_type,
        object_id=badge_factory().id,
        completed_at=now(),
        notification_seen_at=now(),
    )
    # Not completed (no completion timestamp).
    achievement_factory(user=user, content_type=badge_content_type, object_id=badge_factory().id)
    # Pending, but belongs to someone else.
    achievement_factory(
        user=gamma_user_factory(user_uid='someone_else'),
        content_type=badge_content_type,
        object_id=badge_factory().id,
        completed_at=now(),
    )

    response = auth_client.get(reverse('users:api:v0:user-badge-notifications'), {'username': user.user_uid})

    assert [notification['uuid'] for notification in response.json()] == [str(badge_achievement.uuid)]


@pytest.mark.django_db
def test_pending_badge_notifications_excludes_avatar_achievements(
    auth_client, achievement_factory, gamma_user_factory
):
    user = gamma_user_factory(user_uid='avatar_user')
    achievement_factory(
        user=user,
        content_type=ContentType.objects.get_for_model(Avatar),
        object_id=1,
        completed_at=now(),
    )

    response = auth_client.get(reverse('users:api:v0:user-badge-notifications'), {'username': 'avatar_user'})

    assert response.json() == []


@pytest.mark.django_db
def test_pending_badge_notifications_does_not_create_gamma_user(auth_client):
    response = auth_client.get(reverse('users:api:v0:user-badge-notifications'), {'username': 'ghost_user'})

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []
    assert not GammaUser.objects.filter(user_uid='ghost_user').exists()


@pytest.mark.django_db
def test_pending_badge_notifications_requires_username(auth_client):
    response = auth_client.get(reverse('users:api:v0:user-badge-notifications'))

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_pending_badge_notifications_requires_authentication(client):
    response = client.get(reverse('users:api:v0:user-badge-notifications'), {'username': 'whoever'})

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_mark_badge_notifications_seen(auth_client, badge_achievement):
    url = reverse('users:api:v0:user-badge-notifications-seen')

    response = auth_client.post(
        url,
        {'username': 'notified_user', 'uuids': [str(badge_achievement.uuid)]},
        format='json',
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'count': 1}
    badge_achievement.refresh_from_db()
    assert badge_achievement.notification_seen_at is not None

    # Idempotent: a second acknowledgement touches nothing.
    first_seen_at = badge_achievement.notification_seen_at
    response = auth_client.post(
        url,
        {'username': 'notified_user', 'uuids': [str(badge_achievement.uuid)]},
        format='json',
    )
    badge_achievement.refresh_from_db()
    assert response.json() == {'count': 0}
    assert badge_achievement.notification_seen_at == first_seen_at


@pytest.mark.django_db
def test_mark_badge_notifications_seen_scoped_to_user(auth_client, badge_achievement):
    response = auth_client.post(
        reverse('users:api:v0:user-badge-notifications-seen'),
        {'username': 'some_other_user', 'uuids': [str(badge_achievement.uuid)]},
        format='json',
    )

    assert response.json() == {'count': 0}
    badge_achievement.refresh_from_db()
    assert badge_achievement.notification_seen_at is None


@pytest.mark.django_db
def test_mark_badge_notifications_seen_validates_payload(auth_client):
    url = reverse('users:api:v0:user-badge-notifications-seen')

    assert auth_client.post(url, {'username': 'x'}, format='json').status_code == status.HTTP_400_BAD_REQUEST
    assert auth_client.post(
        url, {'username': 'x', 'uuids': []}, format='json'
    ).status_code == status.HTTP_400_BAD_REQUEST
    assert auth_client.post(
        url, {'username': 'x', 'uuids': ['not-a-uuid']}, format='json'
    ).status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_mark_badge_notifications_seen_requires_authentication(client):
    response = client.post(
        reverse('users:api:v0:user-badge-notifications-seen'),
        {'username': 'whoever', 'uuids': ['00000000-0000-0000-0000-000000000000']},
        format='json',
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN

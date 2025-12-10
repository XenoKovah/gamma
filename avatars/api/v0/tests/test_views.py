import pytest

from django.urls import reverse
from rest_framework import status

from avatars.constants import AVATAR_SET_FINISH_FAILURE, AVATAR_SET_FINISH_SUCCESS
from avatars.tests.factories import AvatarFactory, AvatarSetFactory


@pytest.mark.django_db
class TestAvatarSetFinishAction:
    """
    Test case for the testing finishing AvatarSet.
    """

    @pytest.fixture
    def valid_avatar_set(self, avatar_factory: AvatarFactory, avatar_set_factory: AvatarSetFactory):
        avatar_set = avatar_set_factory(title='Test Avatar Set', is_draft=True)
        avatar1 = avatar_factory(title='Avatar 1')
        avatar2 = avatar_factory(title='Avatar 2')
        avatar_set.avatars.set([avatar1, avatar2])
        return avatar_set

    @pytest.fixture
    def invalid_avatar_set(self, avatar_factory: AvatarFactory, avatar_set_factory: AvatarSetFactory):
        avatar_set = avatar_set_factory(title='Invalid Avatar Set', is_draft=True)
        avatar1 = avatar_factory(title='Single Avatar')
        avatar_set.avatars.set([avatar1])
        return avatar_set

    def test_finish_avatar_set_success(self, client, valid_avatar_set):
        url = reverse('avatars:api:v0:avatar_set-finish-avatar-set', kwargs={'pk': valid_avatar_set.id})
        response = client.patch(url)

        valid_avatar_set.refresh_from_db()

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {'message': AVATAR_SET_FINISH_SUCCESS}
        assert valid_avatar_set.is_draft is False

    def test_finish_avatar_set_failure(self, client, invalid_avatar_set):
        url = reverse('avatars:api:v0:avatar_set-finish-avatar-set', kwargs={'pk': invalid_avatar_set.id})
        response = client.patch(url)

        invalid_avatar_set.refresh_from_db()

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {'error': AVATAR_SET_FINISH_FAILURE}
        assert invalid_avatar_set.is_draft is True


@pytest.mark.django_db
class TestUserAvatarConfigViewSet:
    """
    Test case for the testing AvatarConfigViewSet.
    """

    def test_valid_key_secret_authentication(self, live_server, client, app_client):
        url = live_server + reverse('avatars:api:v0:user_avatar_config-list')

        response = client.get(
            url,
            HTTP_APP_KEY=app_client.key,
            HTTP_APP_SECRET=app_client.secret,
        )

        assert response.status_code == status.HTTP_200_OK

    def test_invalid_key_secret_authentication(self, live_server, client):
        url = live_server + reverse('avatars:api:v0:user_avatar_config-list')

        response = client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

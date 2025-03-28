import pytest

from users.api.v0.serializers import GammaUserInfoSerializer
from users.models import GammaUser


@pytest.mark.django_db
class TestGammaUserInfoSerializer:
    """
    Test Case for the testing GammaUserInfoSerializer.
    """

    def test_serializer_with_existing_gamma_user_no_config(self, gamma_user_factory):
        gamma_user = gamma_user_factory(user_uid='test_user')

        serializer = GammaUserInfoSerializer(data={}, context={'user_uid': gamma_user.user_uid})
        serializer.is_valid()
        data = serializer.data

        assert data['gamma_user_id'] == gamma_user.id
        assert data['user_avatar_config'] is None

    def test_serializer_gamma_user_does_not_exist(self):
        assert GammaUser.objects.count() == 0

        username = 'first_gamma_user'
        serializer = GammaUserInfoSerializer(data={}, context={'user_uid': username})
        serializer.is_valid()
        data = serializer.data

        gamma_user = GammaUser.objects.first()

        assert gamma_user.user_uid == username
        assert data['gamma_user_id'] == gamma_user.id
        assert data['user_avatar_config'] is None

    def test_serializer_with_existing_user_and_avatar_set_config(
        self, gamma_user_factory, user_avatar_config_factory
    ):
        gamma_user = gamma_user_factory(user_uid='test_user')
        user_avatar_set_config = user_avatar_config_factory(user=gamma_user)

        serializer = GammaUserInfoSerializer(data={}, context={'user_uid': 'test_user'})
        serializer.is_valid()
        data = serializer.data

        assert data['gamma_user_id'] == gamma_user.id
        assert data['user_avatar_config']['id'] == user_avatar_set_config.id
        assert data['user_avatar_config']['gamma_user_id'] == user_avatar_set_config.user.id
        assert data['user_avatar_config']['selected_avatar_id'] == user_avatar_set_config.selected_avatar.id
        assert data['user_avatar_config']['selected_avatar_set_id'] == user_avatar_set_config.avatar_set.id

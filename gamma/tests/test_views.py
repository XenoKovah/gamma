import pytest
from django.conf import settings
from django.urls import reverse
from rest_framework import status

from core.constants import ADMIN_PERMISSIONS_RESTRICTION


@pytest.mark.django_db
class TestGammaView:
    """
    Tests for permissions to access GammaView.
    """

    def _get_url(self, subpath):
        return reverse('gamma_react_app', kwargs={'subpath': subpath})

    @pytest.mark.parametrize('subpath', ('avatars', 'badges'))
    def test_superuser_and_staff_access(self, subpath, client, user_factory):
        user = user_factory(is_superuser=True, is_staff=True)
        client.force_login(user)

        response = client.get(self._get_url(subpath))

        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.parametrize('subpath', ('avatars', 'badges'))
    def test_superuser_only_access(self, subpath, client, user_factory):
        user = user_factory(is_superuser=True)
        client.force_login(user)

        response = client.get(self._get_url(subpath))

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.content.decode() == ADMIN_PERMISSIONS_RESTRICTION

    @pytest.mark.parametrize('subpath', ('avatars', 'badges'))
    def test_staff_access(self, subpath, client, user_factory):
        user = user_factory(is_staff=True)
        client.force_login(user)

        response = client.get(self._get_url(subpath))

        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.parametrize('subpath', ('avatars', 'badges'))
    def test_regular_user_forbidden(self, subpath, client, user_factory):
        user = user_factory()
        client.force_login(user)

        response = client.get(self._get_url(subpath))

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.content.decode() == ADMIN_PERMISSIONS_RESTRICTION

    @pytest.mark.parametrize('subpath', ('avatars', 'badges'))
    def test_anonymous_user_redirect_to_login(self, subpath, client):
        response = client.get(self._get_url(subpath))

        assert response.status_code == status.HTTP_302_FOUND
        assert settings.LOGIN_URL in response.url

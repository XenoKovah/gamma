import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
def test_user_game_profile_successful(live_server, auth_client):
    url = live_server + reverse('user-gamma-profile')
    user_uid_mock = 'test_user'

    response = auth_client.get(url, {'username': user_uid_mock})
    response_data = response.json()

    expected_keys = {
        'avatar_sets',
        'user_profile',
        'user_avatar_config',
        'system_badges',
        'badges',
        'points',
        'chart',
        'progress',
        'signup_source',
    }

    assert response.status_code == status.HTTP_200_OK
    assert expected_keys.issubset(response_data.keys())


@pytest.mark.django_db
def test_user_game_profile_key_authentication_failed(live_server, client):
    url = live_server + reverse('user-gamma-profile')

    response = client.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {'detail': 'Please provide APP_KEY and APP_SECRET'}


@pytest.mark.django_db
def test_user_game_profile_missing_username(live_server, auth_client):
    url = live_server + reverse('user-gamma-profile')

    response = auth_client.get(url)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'Error': 'user_uid must be set'}

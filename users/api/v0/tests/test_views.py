import pytest
import requests

from django.urls import reverse_lazy
from rest_framework import status


# TODO: add positive test cases when api will be done

@pytest.mark.django_db
def test_user_game_profile_missing_username(live_server, client):
    url = live_server + reverse_lazy('user-gamma-profile')

    response = requests.get(
        url,
        headers={
            'App-key': 'key',
            'App-secret': 'secret',
        },
        verify=False
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'Error': 'user_uid must be set'}

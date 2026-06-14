import pytest
from django.urls import reverse
from rest_framework import status

from leaderboard.api.v0.views import UsersLeaderBoardView
from leaderboard.repository import ORMLeaderboardMemberDataRepository
from users.models import GammaUser

OPT_OUT_URL = 'users:api:v0:user-leaderboard-opt-out'
EXCLUDED_UIDS_URL = 'users:api:v0:leaderboard-excluded-uids'


@pytest.mark.django_db
def test_opt_out_get_defaults_to_not_excluded(auth_client, gamma_user_factory):
    gamma_user_factory(user_uid='learner')

    response = auth_client.get(reverse(OPT_OUT_URL), {'username': 'learner'})

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'excluded': False}


@pytest.mark.django_db
def test_opt_out_get_reflects_flag(auth_client, gamma_user_factory):
    gamma_user_factory(user_uid='hidden', excluded_from_leaderboard=True)

    response = auth_client.get(reverse(OPT_OUT_URL), {'username': 'hidden'})

    assert response.json() == {'excluded': True}


@pytest.mark.django_db
def test_opt_out_get_requires_username(auth_client):
    assert auth_client.get(reverse(OPT_OUT_URL)).status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_opt_out_post_sets_and_clears_flag(auth_client, gamma_user_factory):
    gamma_user_factory(user_uid='learner')

    response = auth_client.post(
        reverse(OPT_OUT_URL), {'username': 'learner', 'excluded': True}, format='json',
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'excluded': True}
    assert GammaUser.objects.get(user_uid='learner').excluded_from_leaderboard

    response = auth_client.post(
        reverse(OPT_OUT_URL), {'username': 'learner', 'excluded': False}, format='json',
    )
    assert response.json() == {'excluded': False}
    assert not GammaUser.objects.get(user_uid='learner').excluded_from_leaderboard


@pytest.mark.django_db
def test_opt_out_post_creates_user_when_missing(auth_client):
    auth_client.post(
        reverse(OPT_OUT_URL), {'username': 'brand_new', 'excluded': True}, format='json',
    )

    assert GammaUser.objects.get(user_uid='brand_new').excluded_from_leaderboard


@pytest.mark.django_db
def test_opt_out_post_validates_payload(auth_client, gamma_user_factory):
    gamma_user_factory(user_uid='learner')
    url = reverse(OPT_OUT_URL)

    assert auth_client.post(
        url, {'excluded': True}, format='json',
    ).status_code == status.HTTP_400_BAD_REQUEST
    assert auth_client.post(
        url, {'username': 'learner', 'excluded': 'yes'}, format='json',
    ).status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_opt_out_requires_authentication(client, gamma_user_factory):
    gamma_user_factory(user_uid='learner')

    assert client.get(
        reverse(OPT_OUT_URL), {'username': 'learner'},
    ).status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_excluded_user_uids_lists_only_opted_out(auth_client, gamma_user_factory):
    gamma_user_factory(user_uid='visible')
    gamma_user_factory(user_uid='hidden_a', excluded_from_leaderboard=True)
    gamma_user_factory(user_uid='hidden_b', excluded_from_leaderboard=True)

    response = auth_client.get(reverse(EXCLUDED_UIDS_URL))

    assert response.status_code == status.HTTP_200_OK
    assert set(response.json()['user_uids']) == {'hidden_a', 'hidden_b'}


@pytest.mark.django_db
def test_collect_user_leaderboards_data_excludes_opted_out(gamma_user_factory):
    gamma_user_factory(user_uid='visible', points=50)
    gamma_user_factory(user_uid='hidden', points=999, excluded_from_leaderboard=True)

    data = ORMLeaderboardMemberDataRepository().collect_user_leaderboards_data()

    uids = {item.user_uid for item in data}
    assert 'visible' in uids
    assert 'hidden' not in uids


@pytest.mark.django_db
def test_rank_users_excludes_opted_out(gamma_user_factory):
    gamma_user_factory(user_uid='visible', points=50)
    gamma_user_factory(user_uid='hidden', points=999, excluded_from_leaderboard=True)

    ranked = UsersLeaderBoardView._rank_users(['visible', 'hidden'], None)

    assert [gamma_user.user_uid for gamma_user in ranked] == ['visible']

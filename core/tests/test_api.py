import requests
import pytest
from rest_framework import status

from achievements.models import StatusBadge
from core.data_models.models import User
from core import db

GAMMA_PROFILE_API_URL = '/api/v0/gamma-profile/'
PROGRESS_API_URL = '/api/v0/progress/'


@pytest.mark.django_db
@pytest.mark.parametrize("need_old_user", [True, False])
def test_api(live_server, rand_str, need_old_user, app_client, event):
    """
    Test setting/getting progress documents.
    """
    user_uid = rand_str
    if need_old_user:
        # Creating User
        db.create_user(User({"user_uid": user_uid}))

    res = requests.put(
        live_server + GAMMA_PROFILE_API_URL,
        data={
            'username': user_uid,
            'event_type': event.event_type,
            'org': rand_str,
            'uid': rand_str
        },
        headers={
            'App-key': app_client.key,
            'App-secret': app_client.secret
        }
    )
    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert data['points'] == event.award

    progress = db.read_progress(user_uid)
    chart = db.read_charted_progress(user_uid)

    assert len(progress) == 1
    for item in progress:
        assert item['points'] == event.award

    assert chart[event.event_type] == {'points': event.award}


@pytest.mark.django_db
def test_uid_required(live_server, rand_str, app_client):
    """
    `uid` field is required.
    """
    res = requests.put(
        live_server + GAMMA_PROFILE_API_URL,
        data={
            'username': rand_str,
            'event_type': rand_str,
            # there is no `uid` field in request
        },
        headers={
            'App-key': app_client.key,
            'App-secret': app_client.secret
        }
    )
    assert res.status_code == 406
    data = res.json()
    assert data['Error'] == 'Event type is not recognizable'


@pytest.mark.django_db
def test_event_not_created(live_server, rand_str, app_client):
    """
    Event should be created in DB.
    """
    res = requests.put(
        live_server + GAMMA_PROFILE_API_URL,
        data={
            'username': rand_str,
            # this event not created in the system
            'event_type': rand_str,
            'uid': rand_str
        },
        headers={
            'App-key': app_client.key,
            'App-secret': app_client.secret
        }
    )
    assert res.status_code == 406
    data = res.json()
    assert data['Error'] == "Event type is not recognizable"


@pytest.mark.django_db
def test_event_repeated(live_server, rand_str, app_client, event):
    """
    Repeated events is not acceptable.
    """
    _ = requests.put(
        live_server + GAMMA_PROFILE_API_URL,
        data={
            'username': rand_str,
            'event_type': rand_str,
            'org': rand_str,
            'uid': rand_str
        },
        headers={
            'App-key': app_client.key,
            'App-secret': app_client.secret
        }
    )
    res = requests.put(
        live_server + GAMMA_PROFILE_API_URL,
        data={
            'username': rand_str,
            'event_type': rand_str,
            'org': rand_str,
            'uid': rand_str
        },
        headers={
            'App-key': app_client.key,
            'App-secret': app_client.secret
        }
    )
    assert res.status_code == 406
    data = res.json()
    assert data['Error'] == 'Repeated event occurs'


@pytest.mark.django_db
def test_put_403(live_server, rand_str):
    """
    Get request for non existent user should return 404.
    """
    res = requests.put(
        live_server + GAMMA_PROFILE_API_URL,
        params={'username': rand_str},
    )
    assert res.status_code == 403
    data = res.json()
    assert data['detail'] == 'Please provide APP_KEY and APP_SECRET'


@pytest.mark.django_db
def test_get(live_server, rand_str, app_client, event):
    """
    Get request should return user game data.
    """
    db.create_user(User({"user_uid": rand_str}))

    # TODO add tests for :points API
    res = requests.get(
        live_server + GAMMA_PROFILE_API_URL,
        params={'username': rand_str},
        headers={
            'App-key': app_client.key,
            'App-secret': app_client.secret
        }
    )
    assert res.status_code == 200
    data = res.json()
    assert data['points'] == 0


@pytest.mark.django_db
def test_get_404(live_server, rand_str, app_client):
    """
    Get request for non existent user should return 200 with zero progress.
    """
    res = requests.get(
        live_server + GAMMA_PROFILE_API_URL,
        params={'username': rand_str},
        headers={
            'App-key': app_client.key,
            'App-secret': app_client.secret
        }
    )
    assert res.status_code == 200
    data = res.json()
    assert data['points'] == 0


@pytest.mark.django_db
def test_get_403( live_server, rand_str):
    """
    Get request for non existent user should return 404.
    """
    res = requests.get(
        live_server + GAMMA_PROFILE_API_URL,
        params={'username': rand_str},
    )
    assert res.status_code == 403
    data = res.json()
    assert data['detail'] == 'Please provide APP_KEY and APP_SECRET'


@pytest.mark.django_db
def test_progress(live_server, rand_str, app_client):
    """
    Get request for `progress` url should return user progress data.
    """
    db.create_user(User({"user_uid": rand_str}))

    res = requests.get(
        live_server + PROGRESS_API_URL,
        params={'username': rand_str},
    )
    assert res.status_code == 200
    data = res.json()
    # TODO add tests for actual data - populate w/ something
    assert isinstance(data, list)


@pytest.mark.django_db
def test_progress_empty(live_server, rand_str, app_client):
    """
    Get request for non existent user should return 404.
    """
    res = requests.get(
        live_server + PROGRESS_API_URL,
        params={'username': rand_str},
        headers={
            'App-key': app_client.key,
            'App-secret': app_client.secret
        }
    )
    assert res.status_code == 200
    data = res.json()
    assert data == []


@pytest.mark.django_db
def test_progress_400(live_server, rand_str, app_client):
    """
    Get request for non existent user should return 404.
    """
    res = requests.get(
        live_server + PROGRESS_API_URL,
        params={'username': ''},
        headers={
            'App-key': app_client.key,
            'App-secret': app_client.secret
        }
    )
    assert res.status_code == 400
    data = res.json()
    assert data['Error'] == 'user_uid must be set'


@pytest.mark.django_db
def test_pointsview(live_server, award, rand_str):
    """
    Test getting points for particular User.
    """
    base_points_url = '/api/v0/points/'
    user_uid = rand_str
    db.create_user(User({"user_uid": rand_str, "points": award}))

    res = requests.get(
        live_server + base_points_url,
        params={'username': user_uid}
    )
    assert res.status_code == 200
    data = res.json()
    assert "user_uid" not in data
    assert data['points'] == award

    res = requests.get(
        live_server + base_points_url,
    )
    assert res.status_code == 400


@pytest.mark.django_db
def test_chartview(live_server, rand_str, app_client, event):
    """
    ChartView should return points by category/event_type.
    """
    _ = requests.put(
        live_server+GAMMA_PROFILE_API_URL,
        data={
            'username': rand_str,
            'event_type': event.event_type,
            'uid': rand_str
        },
        headers={
            'App-key': app_client.key,
            'App-secret': app_client.secret
        }
    )
    res = requests.get(
        live_server+'/api/v0/chart/',
        params={'username': rand_str}
    )
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data[event.event_type], list)
    assert data[event.event_type] == [1, {"points": event.award}]

    res = requests.get(
        live_server+'/api/v0/chart/'
    )
    assert res.status_code == 400
    assert res.json()['Error'] == 'user_uid must be set'


# TODO: test is dependent on integration tests. Need to change this!
def test_badgesview(live_server, rand_str, make_test_file):
    """
    Get Badges for User.
    """
    db.conn.db.badges.drop()  # cleaning badges rules
    db.conn.db.badges.insert_many([
        {
            "slug": "slug_1", 'active': True, 'url': 'sometesturl1',
            'rules': {'actions': {'event_type_1': 2, 'event_type_2': 2}}
        },
        {
            'slug': 'slug_2', 'active': True, 'url': 'sometesturl2',
            'rules': {'actions': {'event_type_1': 1}},
        },
    ])

    db.conn.db.users.drop()  # cleaning users badges data
    badges_data = {
        "slug_1": {
            "progress": {
                "event_type_1": {"count": 2}, "event_type_2": {"count": 1}
            },
            "done": False,
        },
        "slug_2": {
            "progress": {
                "event_type_2": {"count": 1, "goal": 1}
            },
            "done": True,
        },
    }

    db.conn.db.users.replace_one(
        {"user_uid": rand_str},
        {"user_uid": rand_str, "badges": badges_data},
        upsert=True)

    res = requests.get(
        live_server+'/api/v0/badges/',
        params={'username': rand_str}
    )

    assert res.status_code == 200
    data = res.json()

    expected_data = badges_data.copy()

    expected_data['slug_2']['url'] = 'sometesturl2'
    expected_data['slug_2']['dependencies'] = []
    expected_data['slug_2']['title'] = 'slug_2'

    expected_data['slug_1']['url'] = 'sometesturl1'
    expected_data['slug_1']['progress']['event_type_1']['goal'] = 2
    expected_data['slug_1']['progress']['event_type_1']['title'] = 'event_type_1'
    expected_data['slug_1']['progress']['event_type_2']['goal'] = 2
    expected_data['slug_1']['progress']['event_type_2']['title'] = 'event_type_2'
    expected_data['slug_1']['dependencies'] = []
    expected_data['slug_1']['title'] = 'slug_1'

    assert data == expected_data

    _ = requests.get(live_server + '/api/v0/badges/')

    # TODO test deletion, non existing user
    #assert res.status_code == 404
    #assert res.json()['Error'] == 'User not found'


@pytest.mark.django_db
def test_statusview(live_server, rand_str):
    """
    Get all Statuses/Status Badges.
    """
    db.conn.db.statuses.drop()
    statusbadge = StatusBadge(
        title=rand_str,
        slug=rand_str,
        badge_id=rand_str
    )
    statusbadge.save()
    res = requests.get(
        live_server+'/api/v0/statuses/'
    )
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 1
    assert data[0]['title'] == rand_str
    assert data[0]['slug'] == rand_str

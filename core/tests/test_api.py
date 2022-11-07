from datetime import datetime

from django.urls import reverse
import requests
import pytest
from rest_framework import status

from achievements.models import StatusBadge
from core.data_models.models import User, UserEventPoints, Status, Badge
from core import db


GAMMA_PROFILE_API_URL = '/api/v0/gamma-profile/'


@pytest.mark.django_db
@pytest.mark.parametrize("need_old_user", [True, False])
def test_api(live_server, rand_str, need_old_user, app_client, event):
    """
    Test setting/getting progress documents.
    """
    user_uid = rand_str
    if need_old_user:
        # Creating User
        db.users.create(User({"user_uid": user_uid}))

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

    user = db.users.read_one(user_uid)
    progress = user.progress
    chart = user.chart

    progress = progress[str(datetime.now().year)]
    assert len(progress) == 1
    for item in progress:
        assert item.points == event.award

    assert chart[event.event_type] == UserEventPoints({'title': event.title, 'points': event.award})


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
    db.users.create(User({"user_uid": rand_str}))

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
    db.users.create(User({"user_uid": rand_str}))

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
    # TODO add tests for actual data - populate w/ something
    assert isinstance(data, dict)
    assert isinstance(data['progress'], dict)


@pytest.mark.django_db
def test_progress_empty(live_server, rand_str, app_client):
    """
    Get request for non existent user should return 404.
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
    assert data['progress'] == {}


@pytest.mark.django_db
def test_progress_400(live_server, rand_str, app_client):
    """
    Get request for non existent user should return 404.
    """
    res = requests.get(
        live_server + GAMMA_PROFILE_API_URL,
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
def test_pointsview(live_server, award, rand_str, app_client):
    """
    Test getting points for particular User.
    """
    user_uid = rand_str
    db.users.create(User({"user_uid": rand_str, "points": award}))

    res = requests.get(
        live_server + GAMMA_PROFILE_API_URL,
        params={'username': user_uid},
        headers={
            'App-key': app_client.key,
            'App-secret': app_client.secret
        }
    )
    assert res.status_code == 200
    data = res.json()
    assert "user_uid" not in data
    assert data['points'] == award

    res = requests.get(
        live_server + GAMMA_PROFILE_API_URL,
        headers={
            'App-key': app_client.key,
            'App-secret': app_client.secret
        }
    )
    assert res.status_code == 400


@pytest.mark.django_db
def test_chartview(live_server, rand_str, app_client, event):
    """
    ChartView should return points by category/event_type.
    """
    _ = requests.put(
        live_server + GAMMA_PROFILE_API_URL,
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
        live_server + GAMMA_PROFILE_API_URL,
        params={'username': rand_str},
        headers={
            'App-key': app_client.key,
            'App-secret': app_client.secret
        }
    )
    assert res.status_code == 200
    data = res.json()
    chart = data['chart']
    assert chart[event.event_type] == {'title': event.title, "points": event.award}

    res = requests.get(
        live_server + GAMMA_PROFILE_API_URL,
        headers={
            'App-key': app_client.key,
            'App-secret': app_client.secret
        }
    )
    assert res.status_code == 400
    assert res.json()['Error'] == 'user_uid must be set'


# TODO: test is dependent on integration tests. Need to change this!
def test_badgesview(live_server, rand_str, make_test_file, app_client):
    """
    Get Badges for User.
    """
    db.engine.conn.db.badges.drop()  # cleaning badges rules
    active_badges = [
        {
            "badge_uid": "slug_1", "slug": "slug_1", 'active': True, 'url': 'http://badge.url',
            'rules': {'actions': {'event_type_1': 2, 'event_type_2': 2}}
        },
        {
            "badge_uid": "slug_2", 'slug': 'slug_2', 'active': True, 'url': 'http://badge.url',
            'rules': {'actions': {'event_type_1': 1}},
        },
    ]
    unactive_badges = [
        {
            "badge_uid": "slug_3", 'slug': 'slug_3', 'active': False, 'url': 'http://badge.url',
            'rules': {'actions': {'event_type_1': 1}}
        },
        {
            '"badge_uid": "slug_4", slug': 'slug_4', 'active': True, 'url': 'http://badge.url'
        },
        {
            "badge_uid": "slug_5", 'slug': 'slug_5', 'active': True, 'url': 'http://badge.url', 'rules': {}
        },
    ]
    system_badges = active_badges + unactive_badges
    db.engine.conn.db.badges.insert_many(system_badges)

    # Avoid pymongo inset_many side effect
    for badge in system_badges:
        del badge["_id"]

    db.engine.conn.db.users.drop()  # cleaning users badges data
    badges_data = {
        "slug_1": {
            "badge_uid": "slug_1", "title": "title",
            "progress": {
                "event_type_1": {"count": 2}, "event_type_2": {"count": 1}
            },
            "url": "http://badge.url",
            "done": False,
        },
        "slug_2": {
            "badge_uid": "slug_2", "title": "title",
            "progress": {
                "event_type_2": {"count": 1, "goal": 1}
            },
            "url": "http://badge.url",
            "done": True,
        },
    }

    db.engine.conn.db.users.replace_one(
        {"user_uid": rand_str},
        {"user_uid": rand_str, "badges": badges_data},
        upsert=True)

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

    # check only badges that has rules and are active present in system_badges
    assert data["system_badges"] == active_badges
    assert data["badges"] == badges_data


@pytest.mark.django_db
def test_statusview(live_server, rand_str, app_client, make_test_file):
    """
    Get all Statuses/Status Badges.
    """
    db.engine.conn.db.statuses.drop()
    statusbadge = StatusBadge(
        title=rand_str,
        slug=rand_str,
        badge_id=rand_str,
        status_points=99,
        badge_img=make_test_file()
    )
    statusbadge.save()
    db.users.create(User({"user_uid": rand_str}))

    res = requests.get(
        live_server + GAMMA_PROFILE_API_URL,
        params={"username": rand_str},
         headers={
            'App-key': app_client.key,
            'App-secret': app_client.secret
        }
    )
    assert res.status_code == 200
    data = res.json()
    statuses = data["system_statuses"]
    assert len(statuses) == 1
    assert statuses[0]['title'] == rand_str
    assert statuses[0]['status_uid'] == rand_str
    assert statuses[0]['slug'] == rand_str
    assert statuses[0]['url'] == statusbadge.badge_img.url


def _create_statuses(statuses_data):
    for status_data in statuses_data:
        slug = status_data["slug"]
        db.statuses.update(Status({
            "status_uid": slug,
            "slug": slug,
            "title": slug,
            "active": status_data.get('active', True),
            "points": 5,
            "url": f"/test_url/{slug}"
        }))


def _create_badges(badges_data):
    for badge_data in badges_data:
        slug = badge_data["slug"]
        with db.badges.read_and_update(slug) as badge:
            badge.update_badge({
                "badge_uid": slug,
                "slug": slug,
                "title": slug,
                "url": f"/test_url/{slug}",
                "rules": badge_data.get('rules', {}),
                "active": badge_data.get('active', True),
            })


def _setup_dependent_badges_test(live_server):
    """
    Generates a URL for a request.

    The function accepts live_server parameter to generate a URL.
    The function also calls methods to lock records in the
    affected database and blocks other operations until they are completed.
    """
    url = live_server + reverse('api:v0:status-dependent-badges-list')
    db.engine.conn.db.statuses.drop()
    db.engine.conn.db.badges.drop()

    return url


def test_badge_dependent_badges_list_dependencies(live_server, rand_str, app_client):
    """
    Test api for get badge slugs dependent on other badge.
    """
    url = live_server + reverse('api:v0:badge-dependent-badges-list')
    db.engine.conn.db.badges.drop()

    data = [
        {"slug": "b_slug1"},
        {"slug": "b_slug2", "rules": {"badges": ["b_slug1"]}},
        {"slug": "b_slug3", "rules": {"badges": ["b_slug1", "b_slug2"]}},
        {"slug": "b_slug4", "rules": {"badges": ["b_slug1"]}, "active": False},
        {"slug": "b_slug5"},
        {"slug": "b_slug6", "rules": {"badges": ["b_slug5"]}},
    ]
    _create_badges(data)

    resp = requests.get(url, params={"slug": "b_slug1"},)
    assert resp.status_code == 200
    result = set(resp.json())
    # check only active badges dependent on "b_slug1" are in response
    assert result == {"b_slug2", "b_slug3"}


def test_badge_dependent_badges_list_no_dependencies(live_server, rand_str, app_client):
    """
    Test api for get badge slugs dependent on other badge when no dependencies.
    """
    url = live_server + reverse('api:v0:badge-dependent-badges-list')
    db.engine.conn.db.badges.drop()
    data = [
        {"slug": "b_slug1"},
        {"slug": "b_slug2"},
        {"slug": "b_slug3", "rules": {"badges": ["b_slug2"]}},
        {"slug": "b_slug4", "rules": {"badges": ["b_slug3"]}}
    ]
    _create_badges(data)

    resp = requests.get(url, params={"slug": "b_slug1"},)
    assert resp.status_code == 200
    result = resp.json()
    # check response is empty - no dependent badges
    assert result == []


def test_status_dependent_badges_list_dependencies(live_server, rand_str, app_client):
    """
    Test api for get badge slugs dependent on status badge.
    """
    url = _setup_dependent_badges_test(live_server)

    statuses_data = [
        {"slug": "st_slug1"},
        {"slug": "st_slug2"},
        {"slug": "st_slug3"},
    ]
    _create_statuses(statuses_data)
    badges_data = [
        {"slug": "b_slug1", "rules": {"status_badge": "st_slug2"}},
        {"slug": "b_slug2", "rules": {"status_badge": "st_slug1"}},
        {"slug": "b_slug3", "rules": {"status_badge": "st_slug1"}, "active": False},
        {"slug": "b_slug4", "rules": {"status_badge": "st_slug2"}},
    ]
    _create_badges(badges_data)

    resp = requests.get(url, params={"status_badges_slugs": ["st_slug1", "st_slug3"]},)
    assert resp.status_code == 200
    result = resp.json()
    # check only active badges dependent on "st_slug1" are in response
    assert result == {'st_slug1': ['b_slug2']}


def test_status_dependent_badges_list_no_dependencies(live_server, rand_str, app_client):
    """
    Test api for get badge slugs dependent on status badge when no dependencies.
    """
    url = _setup_dependent_badges_test(live_server)

    statuses_data = [
        {"slug": "st_slug1"},
        {"slug": "st_slug2"},
        {"slug": "st_slug3"},
    ]
    _create_statuses(statuses_data)
    badges_data = [
        {"slug": "b_slug1", "rules": {"status_badge": "st_slug2"}},

        {"slug": "b_slug1", "rules": {"status_badge": "st_slug1"}},
        {"slug": "b_slug2", "rules": {"status_badge": "st_slug1"}},
        {"slug": "b_slug3", "rules": {"status_badge": "st_slug1"}},
    ]
    _create_badges(badges_data)

    resp = requests.get(url, params={"status_badges_slugs": ["st_slug2", "st_slug3"]},)
    assert resp.status_code == 200
    result = resp.json()
    # check response is empty - no dependent badges
    assert result == {}


def test_status_dependent_badges_list_empty(live_server, rand_str, app_client):
    """
    Test api for get 400 when there is no data (empty list) in the request.
    """
    url = _setup_dependent_badges_test(live_server)

    statuses_data = [
        {"slug": "st_slug1"},
        {"slug": "st_slug2"},
    ]
    _create_statuses(statuses_data)
    badges_data = [
        {"slug": "b_slug1", "rules": {"status_badge": "st_slug1"}},
        {"slug": "b_slug2", "rules": {"status_badge": "st_slug1"}},
    ]
    _create_badges(badges_data)

    resp = requests.get(url, params={"status_badges_slugs": []},)
    assert resp.status_code == 400


def test_status_dependent_badges_list_no_data(live_server, rand_str, app_client):
    """
    Test api for get 400 when there is no data in the request.
    """
    url = _setup_dependent_badges_test(live_server)

    statuses_data = [
        {"slug": "st_slug1"},
        {"slug": "st_slug2"},
    ]
    _create_statuses(statuses_data)
    badges_data = [
        {"slug": "b_slug1", "rules": {"status_badge": "st_slug2"}},
        {"slug": "b_slug2", "rules": {"status_badge": "st_slug2"}},
    ]
    _create_badges(badges_data)

    resp = requests.get(url, params={},)
    assert resp.status_code == 400

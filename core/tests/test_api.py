from datetime import datetime, timedelta

import requests
import pytest
from django.contrib.auth.models import User
import pymongo

from pointlog.models import LoggedEvent
from achievements.models import UserAchievement, Achievement, StatusBadge
from achievements.services import AchievementRulesMongo, base64_to_file


@pytest.mark.parametrize("need_old_user", [True, False])
def test_api(settings, live_server, rand_str, mongo_conn, need_old_user, app_client, event):
    """
    Test setting/getting progress documents.
    """
    settings.MONGO_DB_NAME = "test-db-{}".format(rand_str)
    if need_old_user:
        # Creating User
        user = User(username=rand_str)
        user.save()

    res = requests.put(
        live_server + '/api/v0/gamma-profile/',
        data={
            'username': rand_str,
            'event_type': event.event_type,
            'org': rand_str,
            'uid': rand_str
        },
        headers={
            'App-key': app_client.key,
            'App-secret': app_client.secret
        }
    )
    assert res.status_code == 200
    data = res.json()
    assert data['points'] == event.award

    if not need_old_user:
        # Get User created during API request
        user = User.objects.get(username=rand_str)

    progress = mongo_conn.get_progress(user)
    chart = mongo_conn.get_charted_progress(user)

    assert progress.count() == 1
    for item in progress:
        assert item['points'] == event.award

    assert chart[event.event_type] == event.award


def test_uniq_id_required(settings, live_server, rand_str, app_client):
    """
    `uniq_id` field is required.
    """
    settings.MONGO_DB_NAME = "test-db-{}".format(rand_str)
    res = requests.put(
        live_server + '/api/v0/gamma-profile/',
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
    assert data['Error'] == 'UID field is mandatory'


def test_event_not_created(settings, live_server, rand_str, app_client):
    """
    Event should be created in DB.
    """
    settings.MONGO_DB_NAME = "test-db-{}".format(rand_str)
    res = requests.put(
        live_server + '/api/v0/gamma-profile/',
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
    assert data['Error'] == 'Event type is not recognizable'


def test_event_repeated(settings, live_server, rand_str, app_client, event):
    """
    Repeated events is not acceptable.
    """
    settings.MONGO_DB_NAME = "test-db-{}".format(rand_str)
    res = requests.put(
        live_server + '/api/v0/gamma-profile/',
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
        live_server + '/api/v0/gamma-profile/',
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

@pytest.mark.skip(reason="App client use id=1")
def test_put_403(settings, live_server, rand_str):
    """
    Get request for non existent user should return 404.
    """
    settings.MONGO_DB_NAME = "test-db-{}".format(rand_str)
    res = requests.put(
        live_server + '/api/v0/gamma-profile/',
        data={'username': rand_str},
    )
    assert res.status_code == 403
    data = res.json()
    assert data['detail'] == 'Please provide APP_KEY and APP_SECRET'

@pytest.mark.skip(reason="App client use id=1")
def test_get(settings, live_server, rand_str, app_client, event):
    """
    Get request should return user game data.
    """
    settings.MONGO_DB_NAME = "test-db-{}".format(rand_str)
    user = User(username=rand_str)
    user.save()

    # TODO add tests for :points API
    res = requests.get(
        live_server + '/api/v0/gamma-profile/',
        data={'username': rand_str},
        headers={
            'App-key': app_client.key,
            'App-secret': app_client.secret
        }
    )
    assert res.status_code == 200
    data = res.json()
    assert data['points'] == 0

@pytest.mark.skip(reason="App client use id=1")
def test_get_404(settings, live_server, rand_str, app_client):
    """
    Get request for non existent user should return 404.
    """
    settings.MONGO_DB_NAME = "test-db-{}".format(rand_str)
    res = requests.get(
        live_server + '/api/v0/gamma-profile/',
        data={'username': rand_str},
        headers={
            'App-key': app_client.key,
            'App-secret': app_client.secret
        }
    )
    assert res.status_code == 404
    data = res.json()
    assert data['Error'] == 'User not found'

@pytest.mark.skip(reason="App client use id=1")
def test_get_403(settings, live_server, rand_str):
    """
    Get request for non existent user should return 404.
    """
    settings.MONGO_DB_NAME = "test-db-{}".format(rand_str)
    res = requests.get(
        live_server + '/api/v0/gamma-profile/',
        data={'username': rand_str},
    )
    assert res.status_code == 403
    data = res.json()
    assert data['detail'] == 'Please provide APP_KEY and APP_SECRET'

@pytest.mark.skip(reason="App client use id=1")
def test_progress(settings, live_server, rand_str, app_client):
    """
    Get request for `progress` url should return user progress data.
    """
    settings.MONGO_DB_NAME = "test-db-{}".format(rand_str)
    user = User(username=rand_str)
    user.save()

    res = requests.get(
        live_server + '/api/v0/progress/',
        params={'username': rand_str},
    )
    assert res.status_code == 200
    data = res.json()
    # TODO add tests for actual data - populate w/ something
    assert isinstance(data, list)


def test_progress_404(settings, live_server, rand_str, app_client):
    """
    Get request for non existent user should return 404.
    """
    settings.MONGO_DB_NAME = "test-db-{}".format(rand_str)
    res = requests.get(
        live_server + '/api/v0/progress/',
        data={'username': rand_str},
        headers={
            'App-key': app_client.key,
            'App-secret': app_client.secret
        }
    )
    assert res.status_code == 404
    data = res.json()
    assert data['Error'] == 'User not found'


def test_eventlog_404(live_server, rand_str, settings):
    """
    Test getting events w/ nonexistent user.
    """
    settings.MONGO_DB_NAME = "test-db-{}".format(rand_str)
    res = requests.get(
        live_server + '/api/v0/logged-event/',
        params={'username': rand_str}
    )
    assert res.status_code == 404
    data = res.json()
    assert data['Error'] == 'User not found'


def test_eventlog(settings, live_server, rand_str, app_client, event):
    """
    Test getting events for last 5 mins.
    """
    settings.MONGO_DB_NAME = "test-db-{}".format(rand_str)
    res = requests.put(
        live_server + '/api/v0/gamma-profile/',
        data={
            'username': rand_str,
            'event_type': event.event_type,
            'org': rand_str,
            'uid': rand_str
        },
        headers={
            'App-key': app_client.key,
            'App-secret': app_client.secret
        }
    )
    # This event should not be returned by API.
    old_event = LoggedEvent(
        user=User.objects.get(username=rand_str),
        uniq_id='some_dummy_test_str',
        event_type=event.event_type,
        points=100,
        client=app_client,
        rewarded_points=8
    )
    old_event.save()
    old_event.date = datetime.now()-timedelta(minutes=6)
    old_event.save()
    res = requests.get(
        live_server + '/api/v0/logged-event/',
        params={'username': rand_str}
    )
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 1
    assert data[0]['event_type'] == event.event_type
    assert data[0]['rewarded_points'] == event.award


def test_pointsview(live_server, admin_user, award, rand_str, settings):
    """
    Test getting points for particular User.
    """
    settings.MONGO_DB_NAME = "test-db-{}".format(rand_str)
    admin_user.gameprofile.points = award
    admin_user.gameprofile.save()
    res = requests.get(
        live_server+'/api/v0/points/',
        params={'username': admin_user.username}
    )
    assert res.status_code == 200
    data = res.json()
    assert data['points'] == award

    res = requests.get(
        live_server+'/api/v0/points/',
    )
    assert res.status_code == 200
    data = res.json()
    assert data['username'] is None
    assert data['points'] == 0

    res = requests.get(
        live_server+'/api/v0/points/',
        params={'username': rand_str}
    )
    assert res.status_code == 200
    data = res.json()
    assert data['username'] == rand_str
    assert data['points'] == 0


def test_chartview(settings, live_server, rand_str, app_client, event):
    """
    ChartView should return points by category/event_type.
    """
    settings.MONGO_DB_NAME = "test-db-{}".format(rand_str)
    res = requests.put(
        live_server+'/api/v0/gamma-profile/',
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
    assert data[event.event_type] == [1, event.award]

    res = requests.get(
        live_server+'/api/v0/chart/'
    )
    assert res.status_code == 404
    assert res.json()['Error'] == 'User not found'


def test_eventpointsview(settings, live_server, rand_str, award, admin_user):
    """
    Emulate rewarding user from admin page.
    """
    settings.MONGO_DB_NAME = "test-db-{}".format(rand_str)
    res = requests.post(
        live_server+'/api/v0/event-points/',
        data={
            'username': admin_user.username,
            'points': award
        }
    )
    res = requests.get(
        live_server+'/api/v0/points/',
        params={'username': admin_user.username}
    )
    assert res.status_code == 200
    data = res.json()
    assert data['points'] == award

    res = requests.post(
        live_server+'/api/v0/event-points/',
        data={
            'username': admin_user.username,
        }
    )
    assert res.status_code == 401
    data = res.json()
    assert data['msg'] == "Requested reward is not valid."


def test_badgesview(live_server, rand_str, event, admin_user, settings):
    """
    Get Badges for User.
    """
    badge_img = base64_to_file('data:image/gif;base64,{}'.format('R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7'))

    # settings.DB_DATA = "test-data-{}".format(rand_str)
    # settings.MONGO_DB_NAME = "test-db-{}".format(rand_str)
    achievement = Achievement(
        title=rand_str,
        slug=rand_str,
        badge_id=event.event_type,
        badge_img=badge_img
    )
    achievement.save()

    user_achiev = UserAchievement(achievement=achievement, user=admin_user)
    user_achiev.save()

    conn = AchievementRulesMongo()
    conn.connect()
    conn.collection.update({'slug': rand_str}, {"$set": {'rules': {}, 'active': True}}, upsert=True)

    res = requests.get(
        live_server+'/api/v0/badges/',
        params={'username': admin_user.username}
    )
    assert res.status_code == 200
    data = res.json()
    # assert len(data) == 1  # db isn't cleaning
    assert bool(data[rand_str]["progress"]) is False
    assert data[rand_str]["done"] is False

    res = requests.get(
        live_server+'/api/v0/badges/'
    )
    assert res.status_code == 404
    assert res.json()['Error'] == 'User not found'


def test_statusview(live_server, rand_str, award, settings):
    """
    Get all Statuses/Status Badges.
    """

    settings.MONGO_DB_NAME = "test-db-{}".format(rand_str)
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

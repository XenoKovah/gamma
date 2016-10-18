import pytest
import requests
from django.contrib.auth.models import User


@pytest.mark.parametrize("need_old_user", [True, False])
def test_api(
    mongo_server,
    settings,
    live_server,
    rand_str,
    mongo_conn,
    need_old_user,
    app_client,
    event
):
    """
    Test setting/getting progress documents.
    """
    settings.MONGODB_CONF = {
        'HOST': 'localhost',
        'PORT': mongo_server,
        'USERNAME': None,
        'PASSWORD': None
    }
    if need_old_user:
        # Creating User
        user = User(username=rand_str)
        user.save()

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


def test_uniq_id_required(mongo_server, settings, live_server, rand_str, app_client):
    """
    `uniq_id` field is required.
    """
    settings.MONGODB_CONF = {
        'HOST': 'localhost',
        'PORT': mongo_server,
        'USERNAME': None,
        'PASSWORD': None
    }
    res = requests.put(
        live_server+'/api/v0/gamma-profile/',
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


def test_event_not_created(mongo_server, settings, live_server, rand_str, app_client):
    """
    Event should be created in DB.
    """
    settings.MONGODB_CONF = {
        'HOST': 'localhost',
        'PORT': mongo_server,
        'USERNAME': None,
        'PASSWORD': None
    }
    res = requests.put(
        live_server+'/api/v0/gamma-profile/',
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


def test_event_not_created(
    mongo_server,
    settings,
    live_server,
    rand_str,
    app_client,
    event
):
    """
    Repeated events is not acceptable.
    """
    settings.MONGODB_CONF = {
        'HOST': 'localhost',
        'PORT': mongo_server,
        'USERNAME': None,
        'PASSWORD': None
    }
    res = requests.put(
        live_server+'/api/v0/gamma-profile/',
        data={
            'username': rand_str,
            'event_type': rand_str,
            'uid': rand_str
        },
        headers={
            'App-key': app_client.key,
            'App-secret': app_client.secret
        }
    )
    res = requests.put(
        live_server+'/api/v0/gamma-profile/',
        data={
            'username': rand_str,
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
    assert data['Error'] == 'Repeated event occurs'


def test_put_403(mongo_server, settings, live_server, rand_str):
    """
    Get request for non existent user should return 404.
    """
    settings.MONGODB_CONF = {
        'HOST': 'localhost',
        'PORT': mongo_server,
        'USERNAME': None,
        'PASSWORD': None
    }
    res = requests.put(
        live_server+'/api/v0/gamma-profile/',
        data={'username': rand_str},
    )
    assert res.status_code == 403
    data = res.json()
    assert data['detail'] == 'Please provide APP_KEY and APP_SECRET'


def test_get(mongo_server, settings, live_server, rand_str, app_client, event):
    """
    Get request should return user game data.
    """
    settings.MONGODB_CONF = {
        'HOST': 'localhost',
        'PORT': mongo_server,
        'USERNAME': None,
        'PASSWORD': None
    }
    user = User(username=rand_str)
    user.save()

    # TODO add tests for :points API
    res = requests.get(
        live_server+'/api/v0/gamma-profile/',
        data={'username': rand_str},
        headers={
            'App-key': app_client.key,
            'App-secret': app_client.secret
        }
    )
    assert res.status_code == 200
    data = res.json()
    assert data['points'] == 0


def test_get_404(mongo_server, settings, live_server, rand_str, app_client):
    """
    Get request for non existent user should return 404.
    """
    settings.MONGODB_CONF = {
        'HOST': 'localhost',
        'PORT': mongo_server,
        'USERNAME': None,
        'PASSWORD': None
    }
    res = requests.get(
        live_server+'/api/v0/gamma-profile/',
        data={'username': rand_str},
        headers={
            'App-key': app_client.key,
            'App-secret': app_client.secret
        }
    )
    assert res.status_code == 404
    data = res.json()
    assert data['Error'] == 'User not found'


def test_get_403(mongo_server, settings, live_server, rand_str):
    """
    Get request for non existent user should return 404.
    """
    settings.MONGODB_CONF = {
        'HOST': 'localhost',
        'PORT': mongo_server,
        'USERNAME': None,
        'PASSWORD': None
    }
    res = requests.get(
        live_server+'/api/v0/gamma-profile/',
        data={'username': rand_str},
    )
    assert res.status_code == 403
    data = res.json()
    assert data['detail'] == 'Please provide APP_KEY and APP_SECRET'


def test_progress(mongo_server, settings, live_server, rand_str, app_client):
    """
    Get request for `progress` url should return user progress data.
    """
    settings.MONGODB_CONF = {
        'HOST': 'localhost',
        'PORT': mongo_server,
        'USERNAME': None,
        'PASSWORD': None
    }
    user = User(username=rand_str)
    user.save()

    res = requests.get(
        live_server+'/api/v0/progress/',
        params={'username': rand_str},
    )
    assert res.status_code == 200
    data = res.json()
    # TODO add tests for actual data - populate w/ something
    assert isinstance(data, list)


def test_progress_404(mongo_server, settings, live_server, rand_str, app_client):
    """
    Get request for non existent user should return 404.
    """
    settings.MONGODB_CONF = {
        'HOST': 'localhost',
        'PORT': mongo_server,
    }

    res = requests.get(
        live_server+'/api/v0/progress/',
        data={'username': rand_str},
        headers={
            'App-key': app_client.key,
            'App-secret': app_client.secret
        }
    )
    assert res.status_code == 404
    data = res.json()
    assert data['Error'] == 'User not found'

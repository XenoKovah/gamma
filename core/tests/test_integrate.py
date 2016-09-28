import pytest

from django.contrib.auth.models import User


# @pytest.fixture
# def selenium(selenium):
#     return selenium


def test_dashboard(live_server, mongo_server, settings, client, rand_str):
    """
    Test dashboard page for logged user.
    """
    settings.MONGODB_CONF = {
        'HOST': 'localhost',
        'PORT': mongo_server,
        'USERNAME': None,
        'PASSWORD': None
    }
    user = User(username=rand_str, password=rand_str)
    user.save()
    client.force_login(user=user)

    res = client.get(live_server.url)
    content = res.content.decode('utf-8')
    assert 'Logout' in content
    assert 'You logged in as user {}.'.format(user.username) in content
    assert 'Congrants, you are in top 100! You rank is 1' in content
    assert 'header-nav-wrap' in content
    assert 'footer' in content


def test_dashboard_anonymous(live_server, client):
    """
    Test dashboard page for anonymous user.
    """
    res = client.get(live_server.url)
    content = res.content.decode('utf-8')
    assert 'Login' in content
    assert 'You need to authenticate in order to see you achievements' in content
    assert 'You logged in as user' not in content
    assert 'Congrants, you are in top 100! You rank is' not in content
    assert 'header-nav-wrap' in content
    assert 'footer' in content

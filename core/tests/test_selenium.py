import pytest


@pytest.fixture
def selenium(selenium):
    return selenium


def test_root(selenium, live_server, mongo_server, settings):
    settings.MONGODB_CONF = {
        'HOST': 'localhost',
        'PORT': mongo_server,
        'USERNAME': None,
        'PASSWORD': None
    }
    selenium.get(live_server.url)

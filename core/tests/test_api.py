import uuid
import random
import string

import pytest
import requests

from core.models import AppClient, Event


@pytest.fixture(scope='function')
def award():
    return random.randint(1, 20)


@pytest.fixture(scope='function')
def rand_str():
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(10))


def test_api(mongo_server, settings, live_server, award, rand_str):
    """
    Test setting/getting progress documents.
    """
    settings.MONGODB_CONF = {
        'HOST': 'localhost',
        'PORT': mongo_server,
        'USERNAME': None,
        'PASSWORD': None
    }
    app_client = AppClient(name=rand_str)
    app_client.save()
    event = Event(event_type=rand_str, award=award)
    event.save()

    res = requests.put(
        live_server+'/gamma-profile/',
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
    assert data['points'] == award

import base64
import random
import string
from datetime import datetime

import pytest
from webpack_loader.loader import WebpackLoader

from django.core.files.base import ContentFile

from core.models import AppClient
from core.notif import push
from core.notif.onesignal_provider import OneSignalServiceBuilder
from core.notif.cfg import Provider

from achievements.models import Event


@pytest.fixture(scope='function')
def award():
    return random.randint(1, 20)


@pytest.fixture(scope='function')
def rand_str():
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(10))


@pytest.fixture(scope='function')
def app_client(rand_str):
    app_cl = AppClient(name=rand_str)
    app_cl.save()
    return app_cl


@pytest.fixture(scope='function')
def event(rand_str, award):
    ev = Event(event_type=rand_str, title=rand_str, award=award)
    ev.save()
    return ev


@pytest.fixture(scope='session')
def current_date():
    return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)


@pytest.fixture(autouse=True)
def no_webpack_loaded(monkeypatch):
    def mockreturn(loader, bundle_name):
        return []
    monkeypatch.setattr(WebpackLoader, "get_bundle", mockreturn)


@pytest.fixture
def make_test_file():
    def _make_test_file(name='image.gif',
                        image_string='R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7'):
        """
        convert base64 attachment string to django File
        :return: django ContentFile
        """
        return ContentFile(base64.b64decode(image_string), name=name)

    return _make_test_file


@pytest.fixture(scope='function')
def push_factory():
    """
    Unregister providers for test purposes.
    """
    factory = push.factory
    factory.register_builder(Provider.ONESIGNAL, OneSignalServiceBuilder())

    yield factory

    factory.unregister_builder(Provider.ONESIGNAL)


@pytest.fixture(scope="function")
def notif_data(mocker):
    """
    Reuser data.
    """
    _heading = "Message heading"
    _content = "Hello username"
    _icon_url = "http://localhost/icon"
    _url = "http://localhost"

    _data = {
        "head": _heading,
        "body": _content,
        "lang": "en",
        "icon": _icon_url,
        "url":  _url
    }

    return _data

@pytest.fixture(scope="function")
def user(mocker):
    _user = mocker.Mock()
    _user.user_uid = "user1"
    _user.player_ids = None

    return _user
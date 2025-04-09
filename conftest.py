import base64
from core.notif.edx_provider import EdxServiceBuilder
import random
import string
from datetime import datetime

import pytest
from pytest_django.fixtures import SettingsWrapper
from pytest_factoryboy import register
from django.core.cache import cache
from django.core.files.base import ContentFile
from redis import Redis
from rest_framework.test import APIClient
from webpack_loader.loader import WebpackLoader

from achievements.tests.factories import AchievementFactory, AchievementRuleFactory
from avatars.factories import AvatarSetFactory, UserAvatarConfigFactory
from badges.factories import BadgeFactory
from core.models import AppClient
from core.data_models.models import User
from core.notif import push
from core.notif.onesignal_provider import OneSignalServiceBuilder
from core.notif.cfg import Provider, Config
from core.notif.utils import get_format_func
from events.factories import EventFactory, EventConfigurationFactory, EventTypeFactory
from rules.factories import RuleFactory
from users.factories import GammaUserCoursePointsFactory, GammaUserFactory


register(AchievementFactory)
register(AchievementRuleFactory)
register(AvatarSetFactory)
register(BadgeFactory)
register(EventFactory)
register(EventTypeFactory)
register(EventConfigurationFactory)
register(GammaUserCoursePointsFactory)
register(GammaUserFactory)
register(RuleFactory)
register(UserAvatarConfigFactory)


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


@pytest.fixture
def client():
    client = APIClient()
    client.credentials(HTTP_CONTENT_TYPE='application/json')
    return client


@pytest.fixture
def auth_client(app_client):
    client = APIClient()
    client.credentials(
        HTTP_APP_KEY=app_client.key,
        HTTP_APP_SECRET=app_client.secret,
        HTTP_CONTENT_TYPE='application/json'
    )
    return client


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
        Convert base64 attachment string to django File.

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
    factory.register_builder(Provider.EDX, EdxServiceBuilder())

    yield factory

    factory.unregister_builder(Provider.ONESIGNAL)
    factory.unregister_builder(Provider.EDX)


@pytest.fixture(scope="function")
def notif_data():
    """
    Reuser data.
    """
    _heading = "Message heading"
    _content = "Hello username"
    _icon_url = "/media/icon.png"
    _url = "http://localhost:9000/performance"

    _data = {
        "head": _heading,
        "body": _content,
        "lang": "en",
        "icon": _icon_url,
        "url":  _url
    }

    return _data


@pytest.fixture(scope="function")
def notif_cfg():
    return {
        Config.ONE_SIGNAL_APP_AUTH_KEY: Config.ONE_SIGNAL_APP_AUTH_KEY,
        Config.ONE_SIGNAL_APP_ID: Config.ONE_SIGNAL_APP_ID,
        Config.WEBPUSHR_KEY: Config.WEBPUSHR_KEY,
        Config.WEBPUSHR_SECRET: Config.WEBPUSHR_SECRET,
        Config.EDX_API_KEY: Config.EDX_API_KEY,
        Config.EDX_NOTIF_FORMAT_FUNC: get_format_func(),
    }


@pytest.fixture(scope="function")
def user():
    _user = User({
        "user_uid": "user1"
    })

    return _user


@pytest.fixture
def redis_client() -> Redis:
    """
    Provide the Redis client.
    """
    return cache.get_client(None)


@pytest.fixture(autouse=True)
def clear_redis_dbs(redis_client) -> None:
    """
    Clear all Redis databases.
    """
    redis_client.flushall()


@pytest.fixture(autouse=True)
def clear_django_cache() -> None:
    """
    Clear Django cache after each test run.
    """
    yield
    cache.clear()


@pytest.fixture(autouse=True)
def temp_media_root(tmpdir_factory: pytest.TempdirFactory, settings: SettingsWrapper) -> "LocalPath":
    """
    Create a temporary directory to store Django media files.
    """
    media_root = tmpdir_factory.mktemp("media_root")
    settings.MEDIA_ROOT = str(media_root)
    return media_root

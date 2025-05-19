import random
import string

import pytest
from pytest_django.fixtures import SettingsWrapper
from pytest_factoryboy import register
from django.core.cache import cache
from redis import Redis
from rest_framework.test import APIClient

from achievements.tests.factories import AchievementFactory, AchievementRuleFactory
from avatars.factories import AvatarSetFactory, UserAvatarConfigFactory
from badges.factories import BadgeFactory
from core.models import AppClient
from events.enums import RggInternalEventTypes
from events.factories import EventFactory, EventConfigurationFactory, EventTypeFactory
from rules.factories import RuleFactory
from users.factories import GammaUserCoursePointsFactory, GammaUserFactory, UserFactory


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
register(UserFactory)


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


@pytest.fixture(autouse=True)
def setup_rgg_internal_events(request, event_type_factory, event_configuration_factory):
    """
    Create internal EventType and EventConfiguration instances using factories.
    """
    if request.node.get_closest_marker('no_rgg_events'):
        return

    for event_name in RggInternalEventTypes.get_all():
        event_type = event_type_factory(name=event_name)
        event_configuration_factory(event_type=event_type)

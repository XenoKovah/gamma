import uuid
import socket
import random
import string
from datetime import datetime

import pytest
import docker as libdocker
from webpack_loader.loader import WebpackLoader

from django.core.cache import cache

from core.services import MongoConnector
from core.models import AppClient
from achievements.models import Event
from edx_integration.api.v2.utils import EVENTS_CACHE_KEY


@pytest.fixture(scope='session')
def unused_port():
    def factory():
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]
    return factory


@pytest.fixture(scope='session')
def session_id():
    return str(uuid.uuid4())


@pytest.fixture(scope='session')
def docker():
    return libdocker.Client(version='auto')


@pytest.yield_fixture(scope='session')
def mongo_server(unused_port, session_id, docker):
    docker.pull('mongo:latest')
    port = unused_port()
    container = docker.create_container(
        image='mongo:latest',
        name='test-mongo-{}'.format(session_id),
        ports=[27017],
        detach=True,
        host_config=docker.create_host_config(
            port_bindings={27017: port}
        )
    )
    docker.start(container=container['Id'])
    yield port
    docker.kill(container=container['Id'])
    docker.remove_container(container['Id'])


@pytest.fixture(scope='session')
def mongo_conn():
    return MongoConnector()


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
    ev = Event(event_type=rand_str, award=award)
    ev.save()
    return ev


@pytest.fixture(scope='session')
def current_date():
    return datetime.strptime(
        str(datetime.now().date()), '%Y-%m-%d'
    )


@pytest.fixture(autouse=True)
def no_webpack_loaded(monkeypatch):
    def mockreturn(loader, bundle_name):
        return []
    monkeypatch.setattr(WebpackLoader, "get_bundle", mockreturn)


@pytest.fixture(scope='function')
def clear_events_cache():
    cache.delete(EVENTS_CACHE_KEY)

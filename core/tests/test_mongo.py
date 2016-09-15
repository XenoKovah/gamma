"""
Module to test mongo setup.
"""

import time
import uuid
import socket

import pytest
import docker as libdocker
from django.core.management import call_command
from django.conf import settings


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
    docker.pull('redis:latest')
    port = unused_port()
    container = docker.create_container(
        image='mongo:latest',
        name='test-mongo-{}'.format(session_id),
        ports=[27017],
        detach=True,
        host_config=docker.create_host_config(
            port_bindings={27017: port}))
    docker.start(container=container['Id'])
    yield port
    docker.kill(container=container['Id'])
    docker.remove_container(container['Id'])


def test_mongo(mongo_server):
    settings.MONGODB_CONF = {
        'HOST': 'localhost',
        'PORT': mongo_server,
        'USERNAME': None,
        'PASSWORD': None
      }
    call_command('mongo_setup')

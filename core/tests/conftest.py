import time
import uuid
import socket
import random
from datetime import datetime

import pytest
import requests
import docker as libdocker


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

import random
from datetime import datetime

import pytest
import pymongo
from django.core.management import call_command

from core.utils import MongoConnector, key_secret_generator


@pytest.fixture(scope='session')
def mongo_conn():
    return MongoConnector()


@pytest.fixture(scope='session')
def current_date():
    return datetime.strptime(
        str(datetime.now().date()), '%Y-%m-%d'
    )


@pytest.fixture(scope='session')
def random_points():
    return random.randint(1, 20)


def test_mongo(mongo_server, settings):
    """
    Testing general mongo flow and `mongo_setup` command.
    """
    settings.MONGODB_CONF = {
        'HOST': 'localhost',
        'PORT': mongo_server,
        'USERNAME': None,
        'PASSWORD': None
    }
    call_command('mongo_setup')


def test_progress(mongo_server, settings, mongo_conn, admin_user, current_date, random_points):
    """
    Test setting/getting progress documents.
    """
    settings.MONGODB_CONF = {
        'HOST': 'localhost',
        'PORT': mongo_server,
        'USERNAME': None,
        'PASSWORD': None
    }
    assert isinstance(mongo_conn.db, pymongo.database.Database)
    mongo_conn.find_one_and_update(
        filter_dict={
            'date': current_date,
            'username': admin_user.username
        },
        key='points',
        value=random_points
    )
    progress = mongo_conn.get_progress(admin_user)
    assert isinstance(progress, pymongo.cursor.Cursor)

    for item in progress:
        assert admin_user.username not in item
        assert item['date'] == current_date
        assert item['points'] == random_points


def test_charted(mongo_server, settings, mongo_conn, admin_user, random_points):
    """
    Test setting/getting charted progress documents.
    """
    settings.MONGODB_CONF = {
        'HOST': 'localhost',
        'PORT': mongo_server,
        'USERNAME': None,
        'PASSWORD': None
    }
    mongo_conn.find_one_and_update(
        filter_dict={
            'username': admin_user.username
        },
        key='video',
        value=random_points,
        event_type='chart'
    )
    charted = mongo_conn.get_charted_progress(admin_user)
    assert isinstance(charted, dict)
    assert admin_user.username not in charted
    assert charted['video'] == random_points


def test_key_gen():
    """
    Test key/secret generator.
    """
    prev = key_secret_generator()
    for i in range(100):
        secret = key_secret_generator()
        assert isinstance(secret, str)
        assert len(secret) >= 15
        assert secret != prev
        prev = secret

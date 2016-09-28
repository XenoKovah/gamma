import pytest
import pymongo
from django.core.management import call_command

from core.models import key_secret_generator
from achievements.services import AchievementRulesMongo


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


def test_progress(mongo_server, settings, mongo_conn, admin_user, current_date, award):
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
        value=award
    )
    progress = mongo_conn.get_progress(admin_user)
    assert isinstance(progress, pymongo.cursor.Cursor)

    assert progress.count() == 1
    for item in progress:
        assert admin_user.username not in item
        assert item['date'] == current_date
        assert item['points'] == award


def test_charted(mongo_server, settings, mongo_conn, admin_user, award):
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
        value=award,
        event_type='chart'
    )
    charted = mongo_conn.get_charted_progress(admin_user)
    assert isinstance(charted, dict)
    assert admin_user.username not in charted
    assert charted['video'] == award


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


def test_rules(mongo_server, rand_str, award):
    """
    Set/get rules by achievement slug.
    """
    storage = AchievementRulesMongo()
    storage.connect()
    storage.upsert_rule(rand_str, {"count": award})
    rules = storage.get_rule(rand_str)

    assert isinstance(rules, dict)
    assert rules['count'] == award


def test_rules(mongo_server, rand_str, award):
    """
    Get non existent achievement slug.
    """
    storage = AchievementRulesMongo()
    storage.connect()
    rules = storage.get_rule(rand_str)

    assert isinstance(rules, type(None))

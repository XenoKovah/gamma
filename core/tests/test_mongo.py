import pytest
import pymongo
from django.core.management import call_command
from django.contrib.auth.models import User

from core.models import key_secret_generator
from achievements.services import AchievementRulesMongo


@pytest.mark.django_db
def test_progress_mongo(settings, mongo_conn, current_date, award, rand_str):
    """
    Test setting/getting progress documents.
    """
    settings.MONGO_DB_NAME = "test-db-{}".format(rand_str)
    user = User.objects.create(username=rand_str)
    assert isinstance(mongo_conn.db, pymongo.database.Database)
    mongo_conn.find_one_and_update(
        filter_dict={
            'date': current_date,
            'username': rand_str
        },
        key='points',
        value=award
    )
    progress = mongo_conn.get_progress(user)
    assert isinstance(progress, pymongo.cursor.Cursor)

    assert progress.count() == 1
    for item in progress:
        assert user.username not in item
        assert item['date'] == current_date
        assert item['points'] == award


@pytest.mark.skip(reason="KeyError: 'video' to fix.")
def test_charted(settings, mongo_conn, admin_user, award, rand_str):
    """
    Test setting/getting charted progress documents.
    """
    settings.MONGO_DB_NAME = "test-db-{}".format(rand_str)
    charted_bf = mongo_conn.get_charted_progress(admin_user)
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
    assert charted['video'] == charted_bf['video'] + award


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


def test_rules(settings, rand_str, award):
    """
    Set/get rules by achievement slug.
    """
    slug = rand_str
    title = slug.upper()
    settings.MONGO_DB_NAME = "test-db-{}".format(rand_str)
    storage = AchievementRulesMongo()
    storage.connect()
    storage.upsert_rule(slug, title, {"count": award})
    rules = storage.get_rule(slug)

    assert isinstance(rules, dict)
    assert rules['count'] == award


def test_rules_none(settings, rand_str, award):
    """
    Get non existent achievement slug.
    """
    settings.MONGO_DB_NAME = "test-db-{}".format(rand_str)
    storage = AchievementRulesMongo()
    storage.connect()
    rules = storage.get_rule(rand_str)

    assert isinstance(rules, type(None))

import pytest

from achievements.models import Event
from core.models import key_secret_generator
from core import db


@pytest.mark.django_db
def test_progress_mongo(current_date, award, rand_str):
    """
    Test setting/getting progress documents.
    """
    user_uid = rand_str
    db.update_user_progress(user_uid, award)

    progress = db.read_progress(user_uid)

    assert isinstance(progress, list)
    assert len(progress) == 1
    assert progress[0]['date'] == current_date
    assert progress[0]['points'] == award

    serialized_progress_item = progress[0].to_primitive('public')
    assert user_uid not in serialized_progress_item
    assert "user_uid" not in serialized_progress_item


@pytest.mark.django_db
def test_charted(award, rand_str):
    """
    Test setting/getting charted progress documents.
    """
    user_uid = rand_str
    event_type = "video"

    Event.objects.create(event_type=event_type, title=event_type, award=award)

    charted_bf = db.read_charted_progress(user_uid)
    assert charted_bf == {}

    db.update_charted_progress(user_uid, "video", award)
    charted = db.read_charted_progress(user_uid)

    assert isinstance(charted, dict)
    assert user_uid not in charted
    assert charted[event_type] == {"points": award}


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


@pytest.mark.django_db
def test_rules(rand_str, award):
    """
    Set/get rules by achievement slug.
    """
    slug = rand_str
    title = slug.upper()
    actions = {"count": award}

    with db.read_badge_and_update(slug) as badge:
        badge.update_badge({
            "title": title, "badge_title": title,
            "rules": {
                "actions": actions
            },
            "url": "test_url"
        })

    rules = db.read_rules(rand_str)

    assert isinstance(rules, dict)
    assert rules['actions']['count'] == award
    assert actions == badge.rules.actions


@pytest.mark.django_db
def test_rules_none(rand_str, award):
    """
    Get non existent achievement slug.
    """
    rules = db.read_rules(rand_str)

    assert isinstance(rules, type(None))

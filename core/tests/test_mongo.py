from datetime import datetime
from random import randint

import pytest  # pylint: disable=import-error
from schematics.exceptions import DataError

from achievements.models import Event
from core.models import key_secret_generator
from core.data_models.models import UserEventPoints
from core import db


@pytest.mark.django_db
def test_progress(current_date, award, rand_str):
    """
    Test setting/getting progress documents.
    """
    user_uid = rand_str
    signup_source = "test-site.com"

    # We want to test that Progress works for repeated awards
    repeated_awards = randint(2, 10)

    for _ in range(repeated_awards):
        db.users.update_progress(user_uid, award, signup_source)

    user = db.users.read_one(user_uid)
    progress = user.progress[str(datetime.now().year)]

    assert isinstance(progress, list)
    assert len(progress) == 1
    assert progress[0]['date'] == current_date
    assert progress[0]['points'] == award * repeated_awards

    serialized_progress_item = progress[0].to_primitive('public')
    assert user_uid not in serialized_progress_item
    assert "user_uid" not in serialized_progress_item


@pytest.mark.django_db
def test_random_award_progress(current_date, rand_str):
    """
    Test setting/getting progress documents.
    """
    user_uid = rand_str
    signup_source = "test-site.com"

    # We want to test that Progress works for repeated awards
    repeated_awards = randint(2, 10)
    total_award = 0

    for _ in range(repeated_awards):
        award = randint(1, 20)
        db.users.update_progress(user_uid, award, signup_source)
        total_award += award

    user = db.users.read_one(user_uid)
    progress = user.progress[str(datetime.now().year)]

    assert isinstance(progress, list)
    assert len(progress) == 1
    assert progress[0]['date'] == current_date
    assert progress[0]['points'] == total_award


@pytest.mark.django_db
def test_charted(award, rand_str):
    """
    Test setting/getting charted progress documents.
    """
    user_uid = event_title = rand_str
    event_type = "video"
    signup_source = "test-site.com"
    Event.objects.create(event_type=event_type, title=event_type, award=award)

    charted_bf = db.users.read_one(user_uid).chart
    assert charted_bf == {}

    db.users.update_chart(user_uid, "video", award, event_title, signup_source)
    charted = db.users.read_one(user_uid).chart

    assert isinstance(charted, dict)
    assert user_uid not in charted  # pylint: disable=unsupported-membership-test
    assert charted[event_type] == UserEventPoints({'title': event_title, "points": award})


@pytest.mark.django_db
def test_update_event_title_in_charts(award, rand_str):
    """
    Testing the function update_event_title_in_charts.
    """
    user_uid = event_title = rand_str
    signup_source = "test-site.com"
    event_type = "course"
    db.users.update_chart(user_uid, event_type, award, event_title, signup_source)
    new_event_title = f'new_{event_title}'
    db.users.update_event_title_in_charts(event_type, new_event_title)

    assert (db.users.read_one(user_uid).chart[event_type] ==
            UserEventPoints({'title': new_event_title, "points": award}))


@pytest.mark.django_db
def test_change_event_title(award, rand_str):
    """
    Test changing the Event title will also change it in user charts.
    """
    user_uid = event_title = rand_str
    signup_source = "test-site.com"
    event_type = "course"

    Event.objects.create(event_type=event_type, title=event_title, award=award)
    db.users.update_chart(user_uid, event_type, award, event_title, signup_source)
    assert (db.users.read_one(user_uid).chart[event_type] ==
           UserEventPoints({'title': event_title, "points": award}))

    obj = Event.objects.get(event_type=event_type)
    obj.title = f'new_{event_title}'
    obj.save()

    assert (db.users.read_one(user_uid).chart[event_type] ==
           UserEventPoints({'title': f'new_{event_title}', "points": award}))


def test_key_gen():
    """
    Test key/secret generator.
    """
    prev = key_secret_generator()
    for i in range(100):  # pylint: disable=unused-variable
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

    with db.badges.read_and_update(slug) as badge:
        badge.update_badge({
            "title": title,
            "rules": {
                "actions": actions
            },
            "url": "http://test_url"
        })

    rules = db.badges.read_rules(rand_str)

    assert isinstance(rules, dict)
    assert rules['actions']['count'] == award
    assert actions == badge.rules.actions


@pytest.mark.xfail(raises=DataError)
def test_rules(rand_str, award):  # pylint: disable=function-redefined)
    """
    Set/get rules by achievement slug.
    """
    slug = rand_str
    title = slug.upper()
    actions = {"count": award}

    with db.badges.read_and_update(slug) as badge:
        badge.update_badge({
            "title": title,
            "rules": {
                "actions": actions
            },
            "url": "/test_url"
        })


@pytest.mark.django_db
def test_rules_none(rand_str, award):
    """
    Get non existent achievement slug.
    """
    rules = db.badges.read_rules(rand_str)

    assert isinstance(rules, type(None))

import pytest

from achievements.models import Achievement, StatusBadge
from core import db


@pytest.mark.django_db
def test_deleted_badge_deactivated(make_test_file):
    slug = 'badgeslug1'
    achiev = Achievement.objects.create(title=slug, slug=slug, badge_img=make_test_file())
    badge_mongo = db.badges.read_one(slug)
    assert badge_mongo.badge_uid == slug
    assert badge_mongo.active is True
    achiev.delete()
    badge_mongo = db.badges.read_one(slug)
    assert badge_mongo.badge_uid == slug
    assert badge_mongo.active is False


@pytest.mark.django_db
def test_deactivated_badge_creation(make_test_file):
    slug = 'badgeslug1'
    achiev = Achievement.objects.create(title=slug, slug=slug, badge_img=make_test_file())

    rules = {'actions': {'fakeevent': 2}, 'badges': ['fakebadge'], 'status_badge': 'fakestatus'}
    with db.badges.read_and_update(slug) as badge:
        badge.update_badge({'rules': rules})
    badge_mongo = db.badges.read_one(slug)
    # check rules are set before deactivation
    assert badge_mongo.rules.to_primitive() == rules

    # Delete badge and than create badge with the same slug
    achiev.delete()
    achiev = Achievement.objects.create(title=slug, slug=slug, badge_img=make_test_file())
    badge_mongo = db.badges.read_one(slug)
    assert badge_mongo.badge_uid == slug
    assert badge_mongo.active is True
    # check old rules are cleared after recreation
    assert not badge_mongo.rules


@pytest.mark.django_db
def test_deleted_status_deactivated(make_test_file):
    slug = 'statusslug1'
    status = StatusBadge.objects.create(title=slug, slug=slug, badge_img=make_test_file(), status_points=10)
    status_mongo = db.statuses.read_one(slug)
    assert status_mongo.status_uid == slug
    assert status_mongo.active is True
    status.delete()
    status_mongo = db.statuses.read_one(slug)
    assert status_mongo.status_uid == slug
    assert status_mongo.active is False


@pytest.mark.django_db
def test_deactivated_status_creation(make_test_file):
    slug = 'statusslug1'
    status = StatusBadge.objects.create(title=slug, slug=slug, badge_img=make_test_file(), status_points=15)
    status.delete()
    # Delete status and than create status with the same slug
    status = StatusBadge.objects.create(title=slug, slug=slug, badge_img=make_test_file(), status_points=20)
    status_mongo = db.statuses.read_one(slug)
    assert status_mongo.status_uid == slug
    assert status_mongo.active is True
    assert status_mongo.points == 20

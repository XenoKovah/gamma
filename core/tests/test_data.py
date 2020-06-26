import pytest

from achievements.models import Achievement, StatusBadge
from core import db


@pytest.mark.django_db
def test_deleted_badge_deactivated(make_test_file):
    slug = 'badgeslug1'
    achiev = Achievement.objects.create(title=slug, slug=slug, badge_img=make_test_file())
    badge_mongo = db.badges.read_one_as_ob(slug)
    assert badge_mongo.badge_uid == slug
    assert badge_mongo.active is True
    achiev.delete()
    badge_mongo = db.badges.read_one_as_ob(slug)
    assert badge_mongo.badge_uid == slug
    assert badge_mongo.active is False


@pytest.mark.django_db
def test_deactivated_badge_creation(make_test_file):
    slug = 'badgeslug1'
    achiev = Achievement.objects.create(title=slug, slug=slug, badge_img=make_test_file())
    # Delete badge and than create badge with the same slug
    achiev.delete()
    achiev = Achievement.objects.create(title=slug, slug=slug, badge_img=make_test_file())
    badge_mongo = db.badges.read_one_as_ob(slug)
    assert badge_mongo.badge_uid == slug
    assert badge_mongo.active is True


@pytest.mark.django_db
def test_deleted_status_deactivated(make_test_file):
    slug = 'statusslug1'
    status = StatusBadge.objects.create(title=slug, slug=slug, badge_img=make_test_file())
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
    status = StatusBadge.objects.create(title=slug, slug=slug, badge_img=make_test_file())
    status.delete()
    # Delete status and than create status with the same slug
    status = StatusBadge.objects.create(title=slug, slug=slug, badge_img=make_test_file())
    status_mongo = db.statuses.read_one(slug)
    assert status_mongo.status_uid == slug
    assert status_mongo.active is True

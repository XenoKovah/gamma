from bson import ObjectId
from contextlib import contextmanager

from schematics.exceptions import DataError

from core.data_models.models import Badge
from core.db.engine import conn


def _create_badge_ob(data) -> Badge:
    try:
        badge = Badge().import_data(data)
    except DataError:
        # TODO: add logging
        badge = None
    return badge


def _update(badge):
    """
    Update Bagde document.
    """
    data = badge.to_native()
    badge_id = data.pop('_id')

    conn.db.badges.find_one_and_replace(
        {
            '_id': ObjectId(badge_id),
        },
        data,
        upsert=True
    )


def read_rules(achievement_slug):
    """
    Return rules for particular achievement.
    """
    badge = conn.db.badges.find_one({'slug': achievement_slug})
    return badge.get('rules') if badge else None


def activate(badge_uid):
    """
    Activate badge.
    """
    conn.db.badges.update_one(
        filter={'slug': badge_uid},
        update={'$set': {'active': True}})


def deactivate(badge_uid):
    """
    Deactivate badge.
    """
    conn.db.badges.update_one(
        filter={'slug': badge_uid},
        update={'$set': {'active': False}})


def read_active():
    """
    Read all active badges from db.
    """
    return [_create_badge_ob(badge) for badge in conn.db.badges.find({"active": True})]


def update_skeleton(badge):
    """
    Update badge core data.

    badge: badge
    """
    conn.db.badges.update_one(
        {"badge_uid": badge.badge_uid},
        {"$set": badge.to_native('skeleton')},
        upsert=True
    )


def read_one(badge_uid):
    """
    Read badge from db by badge_uid.
    """
    # TODO: change slug to badge_uid
    return conn.db.badges.find_one({"slug": badge_uid}, {"_id": 0}) or {}


def read_one_as_ob(badge_uid):
    data = conn.db.badges.find_one({"slug": badge_uid})
    return _create_badge_ob(data)


@contextmanager
def read_and_update(badge_uid):
    """
    Read badge from db by badge_uid.
    """
    # TODO: change slug to badge_uid

    if data := conn.db.badges.find_one({"slug": badge_uid}):
        badge = _create_badge_ob(data)
    else:
        badge = Badge({"badge_uid": badge_uid, "slug": badge_uid})

    yield badge

    _update(badge)

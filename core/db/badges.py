import logging
from typing import List
from contextlib import contextmanager

from bson import ObjectId
from schematics.exceptions import DataError

from core.data_models.models import Badge
from core.db.engine import conn


LOG = logging.getLogger(__name__)


def _create_ob(data) -> Badge:
    try:
        badge = Badge(data, strict=False)
    except DataError as ex:
        badge = None
        LOG.error(f"Can't import Badge data {ex} for badge: {data.get('badge_uid')}")
    return badge


def _update(badge):
    """
    Update Bagde document.
    """
    badge.validate()

    data = badge.to_native()
    badge_id = data.pop('_id')

    conn.db.badges.replace_one(
        {
            '_id': ObjectId(badge_id),
        },
        data,
        upsert=True
    )


def read_rules(badge_uid):
    """
    Return rules for particular achievement.
    """
    badge = conn.db.badges.find_one({'badge_uid': badge_uid})
    return badge.get('rules') if badge else None


def activate(badge_uid):
    """
    Activate badge.
    """
    conn.db.badges.update_one(
        filter={'badge_uid': badge_uid},
        update={'$set': {'active': True}})


def deactivate(badge_uid):
    """
    Deactivate badge.
    """
    conn.db.badges.update_one(
        filter={'badge_uid': badge_uid},
        update={'$set': {'active': False}})


def read_active():
    """
    Read all active badges from db.
    """
    data = [_create_ob(badge) for badge
            in conn.db.badges.find({"active": True,
                     "$and": [{"rules": {"$exists": True}},
                              {"rules": {"$ne": {}}},
                              {"rules": {"$ne": None}}]})]

    # temporarly workaround to exclude None objects
    return [badge for badge in data if badge]


def read(_filter=None) -> List[Badge]:
    data = [_create_ob(data) for data in conn.db.badges.find(_filter)]

    # temporarly workaround to exclude None objects
    return [badge for badge in data if badge]


def update_skeleton(badge):
    """
    Update badge core data.

    badge: badge
    """
    badge.validate()

    conn.db.badges.update_one(
        {"badge_uid": badge.badge_uid},
        {"$set": badge.to_native('skeleton')},
        upsert=True
    )


def read_one(badge_uid):
    data = conn.db.badges.find_one({"badge_uid": badge_uid})
    return _create_ob(data)


@contextmanager
def read_and_update(badge_uid):
    """
    Read badge from db by badge_uid.
    """
    if data := conn.db.badges.find_one({"badge_uid": badge_uid}):
        badge = _create_ob(data)
    else:
        badge = Badge({"badge_uid": badge_uid, "slug": badge_uid})

    yield badge

    _update(badge)

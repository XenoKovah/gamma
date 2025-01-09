import logging
from typing import List
from contextlib import contextmanager

from bson import ObjectId
from schematics.exceptions import DataError

from core.data_models.models import Badge


log = logging.getLogger(__name__)


class BadgesRepository:

    def __init__(self, db):
        self.db = db

    def _create_ob(data) -> Badge:
        try:
            badge = Badge(data, strict=False)
        except DataError as ex:
            badge = None
            log.error(f"Can't import Badge data {ex} for badge: {data.get('badge_uid')}")  # pylint: disable=logging-fstring-interpolation
        return badge

    def _update(self, badge):
        """
        Update Bagde document.
        """
        badge.validate()

        data = badge.to_native()
        badge_id = data.pop('_id')

        self.db.badges.replace_one(
            {
                '_id': ObjectId(badge_id),
            },
            data,
            upsert=True
        )

    def read_rules(self, badge_uid):
        """
        Return rules for particular achievement.
        """
        badge = self.db.badges.find_one({'badge_uid': badge_uid})
        return badge.get('rules') if badge else None

    def activate(self, badge_uid):
        """
        Activate badge.
        """
        self.db.badges.update_one(
            filter={'badge_uid': badge_uid},
            update={'$set': {'active': True}})

    def deactivate(self, badge_uid):
        """
        Deactivate badge.
        """
        self.db.badges.update_one(
            filter={'badge_uid': badge_uid},
            update={'$set': {'active': False}})

    def read_active(self):
        """
        Read all active badges from db.
        """
        data = [self._create_ob(badge) for badge
                in self.db.badges.find({
                    "active": True,
                    "$and": [
                        {"rules": {"$exists": True}},
                        {"rules": {"$ne": {}}},
                        {"rules": {"$ne": None}}
                    ]
                })]

        # temporarly workaround to exclude None objects
        return [badge for badge in data if badge]

    def read(self, _filter=None) -> List[Badge]:
        data = [self._create_ob(data) for data in self.db.badges.find(_filter)]

        # temporarly workaround to exclude None objects
        return [badge for badge in data if badge]

    def update_skeleton(self, badge):
        """
        Update badge core data.

        badge: badge
        """
        badge.validate()

        self.db.badges.update_one(
            {"badge_uid": badge.badge_uid},
            {"$set": badge.to_native('skeleton')},
            upsert=True
        )

    def read_one(self, badge_uid):
        data = self.db.badges.find_one({"badge_uid": badge_uid})
        return self._create_ob(data)

    @contextmanager
    def read_and_update(self, badge_uid):
        """
        Read badge from db by badge_uid.
        """
        if data := self.db.badges.find_one({"badge_uid": badge_uid}):
            badge = self._create_ob(data)
        else:
            badge = Badge({"badge_uid": badge_uid, "slug": badge_uid})

        yield badge

        self._update(badge)

    def dependent_badges(self, badge_uid):
        """
        Return list of active badges uids that depend on specified badge.
        """
        return [
            badge['badge_uid'] 
            for badge in self.db.badges.find({"active": True, "rules.badges": badge_uid}, {"badge_uid": 1, "_id": 0})
        ]

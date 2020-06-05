import os
from bson import ObjectId
from datetime import datetime
from contextlib import contextmanager

import pymongo
from pymongo import WriteConcern, ReturnDocument, DESCENDING
from schematics.exceptions import DataError

from core.data_models.models import (
    DailyProgress,
    User,
    Leaders,
    Status,
    SystemEvent,
    AppClient,
    Badge,
)


EVENT_HISTORY_DB_INDEXES = [("uid", pymongo.ASCENDING),
                            ("user_uid", pymongo.ASCENDING),
                            ("client", pymongo.ASCENDING)]

USERS_INDEXES = [("user_uid", pymongo.ASCENDING)]


class Singleton(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance


class MongoConnector(Singleton):
    """
    Mongo connector as singleton object to utilize
    mongo connection pool.
    """
    _db = None

    @property
    def db(self):
        if not self._db:
            mongo_database = os.getenv('MONGO_DATABASE')
            assert mongo_database
            self._mongo_init(mongo_database)
        return self._db

    def _mongo_init(self, mongo_database):
        """
        Set class _db variable.
        """
        mongo_url = os.getenv('MONGO_URL')
        assert mongo_url

        client = pymongo.MongoClient(mongo_url)

        self._db = client[mongo_database]

        self._db.users.create_index(USERS_INDEXES, unique=True)
        self._db.event_history.create_index(EVENT_HISTORY_DB_INDEXES, unique=True)

conn = MongoConnector()


def _create_user_ob(data) -> User:
    return User().import_data(data)


def _create_badge_ob(data) -> Badge:
    try:
        badge = Badge().import_data(data)
    except DataError:
        # TODO: add logging
        badge = None
    return badge


def _create_status_ob(data) -> Status:
    try:
        status = Status().import_data(data)
    except DataError:
        status = None
    return status


def _create_event_ob(data) -> SystemEvent:
    return SystemEvent().import_data(data)


def _create_app_client_ob(data) -> AppClient:
    try:
        app_client = AppClient().import_data(data)
    except DataError:
        app_client = None
    return app_client


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


def _update_user(user):
    """
    Update User document.
    """
    data = user.to_native()
    user_id = data.pop('_id')

    conn.db.users.find_one_and_replace(
        {
            '_id': ObjectId(user_id),
        },
        data,
        upsert=True
    )


def update_user_progress(user_uid, event_award):
    """
    Update user progress with points for a particular date.
    """
    year = datetime.now().year
    date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    daily_progress = DailyProgress({"date": date, "points": event_award})

    if conn.db.users.find_one({"user_uid": user_uid,
                              f"progress.{year}.date": date}, {"_id": 1}):
        conn.db.users.update_one(
            filter={"user_uid": user_uid, f"progress.{year}.date": date},
            update={
                "$inc": {
                    f"progress.{year}.$.points": event_award
                }
            })

    else:
        conn.db.users.update_one(
            filter={"user_uid": user_uid},
            update={
                "$addToSet": {
                    f"progress.{year}": daily_progress.to_primitive()
                }
            }, upsert=True)


def read_progress(user_uid: str):
    """
    Get progress data from MongoDB.

    user_uid: username unique id
    """
    year = datetime.now().year
    user = read_user(user_uid)

    return user.progress.get(str(year), [])


def update_charted_progress(user_uid, event_type, event_award):
    """
    Update user chart with points for a particular event type.
    """
    conn.db.users.update_one(
        filter={"user_uid": user_uid},
        update={"$inc": {f"chart.{event_type}.points": event_award}},
        upsert=True)

def read_charted_progress(user_uid):
    """
    Return charts for user progress.
    """
    chart = {}
    if (_ := conn.db.users.find_one({"user_uid": user_uid}, {"chart": 1, "_id": 0})):
        chart = _.get("chart", {})

    events = read_events()
    events = [_.event_type for _ in events]

    for event in chart.copy().keys():
        if event not in events:
            chart.pop(event)

    return chart


def read_rules(achievement_slug):
    """
    Return rules for particular achievement.
    """
    badge = conn.db.badges.find_one({'slug': achievement_slug})
    return badge.get('rules') if badge else None


def activate_badge(badge_uid):
    """
    Activate badge.
    """
    conn.db.badges.update_one(
        filter={'slug': badge_uid},
        update={'$set': {'active': True}})


def deactivate_badge(badge_uid):
    """
    Deactivate badge.
    """
    conn.db.badges.update_one(
        filter={'slug': badge_uid},
        update={'$set': {'active': False}})


def read_active_badges():
    """
    Read all active badges from db.
    """
    return conn.db.badges.find({"active": True})


def read_statuses():
    """
    Read all system statuses.
    """
    return [_create_status_ob(status) for
        status in conn.db.statuses.find({"active": True})]

def read_status(status_uid):
    """
    Read all user statuses.
    """
    data = conn.db.statuses.find_one({"status_uid": status_uid})
    return _create_status_ob(data)

def read_user_statuses(user_uid):
    """
    Read all user statuses.
    """
    user = read_user(user_uid)
    return [_create_status_ob(status) for status in user.get("statuses")]


def read_user_status(user_uid, status_uid):
    """
    Read all user statuses.
    """
    return conn.db.users.find_one({"user_uid": user_uid, "statuses.status_uid": status_uid})


def read_events():
    """
    Read all accepted events.
    """
    return [_create_event_ob(event) for event in conn.db.events.find()]


def read_system_event(event_type):
    """
    Read system event.
    """
    event = {}
    if data := conn.db.events.find_one({"event_type": event_type}):
        event = _create_event_ob(data)
    return event


def update_event(system_event):
    """
    Update event.

    system_event: SystemEvent
    """
    conn.db.events.update_one(
        {"event_type": system_event.event_type},
        {"$set": system_event.to_native()},
        upsert=True
    )


def update_badge_skeleton(badge):
    """
    Update badge core data.

    badge: badge
    """
    conn.db.badges.update_one(
        {"badge_uid": badge.badge_uid},
        {"$set": badge.to_native('skeleton')},
        upsert=True
    )


def read_badge(badge_uid):
    """
    Read badge from db by badge_uid.
    """
    # TODO: change slug to badge_uid
    return conn.db.badges.find_one({"slug": badge_uid}, {"_id": 0}) or {}


def read_badge_as_ob(badge_uid):
    data = conn.db.badges.find_one({"slug": badge_uid})
    return _create_badge_ob(data)


@contextmanager
def read_badge_and_update(badge_uid):
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


@contextmanager
def read_user_and_update(user_uid):
    """
    Read user from db by user_uid.
    """
    if data := conn.db.users.find_one({"user_uid": user_uid}):
        user = _create_user_ob(data)
    else:
        user = User({"user_uid": user_uid})

    yield user

    _update_user(user)


def update_game_profile(user_uid, points) -> int:
    """
    Update user game profile with points.

    Returns: points AFTER increment.
    """
    user = conn.db.users.find_one_and_update(
        {"user_uid": user_uid},
        {"$inc": {"points": points}},
        return_document=ReturnDocument.AFTER,
        upsert=True)

    return user.get("points", 0)


def create_user(user):
    """
    Create blank user.

    Actually just a helper function.
    """
    conn.db.users.insert_one(user.to_native())


def update_user_status(user_uid, points):
    """
    Assign all matched statuses.
    """
    for status in matched_statuses(points):
        conn.db.users.update_one(
            {"user_uid": user_uid}, {"$addToSet": {"statuses": status.to_native('client')}})



def matched_statuses(points):
    """
    Returns all status matched statuses.
    """
    return [_create_status_ob(status) for
        status in conn.db.statuses.find(
            {"active": True, "status_points": {"$lte": points}})]


def get_status_achieved(prev_points, new_points):
    """
    Return top status that can be achieved between two points.

    Return None if specified status does not exist.
    """
    res = list(
        conn.db.statuses.find(
            {"active": True, "status_points": {"$gt": prev_points, "$lte": new_points}}
        ).sort([("status_points", -1)]).limit(1))
    return res[0]['status_uid'] if res else None


def update_status(status):
    """
    Update/upsert status badge.

    status: Status model
    """
    conn.db.statuses.update_one(
        {"status_uid": status.status_uid},
        {"$set": status.to_native()},
        upsert=True
    )


def read_user(user_uid):
    """
    Read user/game_profile from db.
    """
    return _create_user_ob(conn.db.users.find_one({"user_uid": user_uid}) or {"user_uid": user_uid})


def log_event(event):
    """
    Check event before saving.

    Return None in case of duplicated event.
    """
    if conn.db.event_history.find_one({"uid": event.uid, "user_uid": event.username, "client": event.client}):
        return None

    conn.db.event_history.with_options(write_concern=WriteConcern(w=0)).insert_one(event.to_native())

    return event


def read_user_badges(user_uid):
    """
    Read all game profile badges.

    It can be achieved badge of badge in progress.
    """
    data = conn.db.users.find_one({"user_uid": user_uid}, {"badges": 1, "_id": 0}) or {}
    return data.get('badges', {})


def update_user_badge(user_uid, badge_uid, badge_url, progress, done, upsert):
    conn.db.users.update_one(
        {"user_uid": user_uid},
        {
            "$set": {
                f"badges.{badge_uid}.progress": progress,
                f"badges.{badge_uid}.done": done,
                f"badges.{badge_uid}.url": badge_url
            }
        },
        upsert=upsert
    )


def read_leaders():
    """
    Read top 100 users based on points field.
    """
    return Leaders().import_data({"roster": conn.db.users.find({}).sort([("points", DESCENDING)]).limit(100)})


def update_app_client(app_client):
    """
    Update AppClient model.
    """
    conn.db.app_clients.update_one(
        {"uid": app_client.uid},
        {"$set": app_client.to_native('internal')},
        upsert=True)


def read_app_client(key, secret):
    data = conn.db.app_clients.find_one({"key": key, "secret": secret})
    return _create_app_client_ob(data)


def health():
    """
    Health check for MongoDB.

    Do ping and serverStatus commands.
    """
    return conn.db.command('ping'), conn.db.command('serverStatus')

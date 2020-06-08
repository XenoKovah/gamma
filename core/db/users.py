from bson import ObjectId
from datetime import datetime
from contextlib import contextmanager

from pymongo import ReturnDocument
from schematics.exceptions import DataError

from core.data_models.models import (
    DailyProgress,
    User,
    Status,
)

from core.db.engine import conn


def _create_status_ob(data) -> Status:
    try:
        status = Status().import_data(data)
    except DataError:
        status = None
    return status


def _update(user):
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

def _create_ob(data) -> User:
    return User().import_data(data)



def update_profile(user_uid, event):
    update_progress(user_uid, event.points)
    update_chart(user_uid, event.event_type, event.points)
    points = update_points(user_uid, event.points)

    return points



def update_progress(user_uid, event_award):
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


def update_chart(user_uid, event_type, event_award):
    """
    Update user chart with points for a particular event type.
    """
    conn.db.users.update_one(
        filter={"user_uid": user_uid},
        update={"$inc": {f"chart.{event_type}.points": event_award}},
        upsert=True)


def update_points(user_uid, points) -> int:
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


@contextmanager
def read_and_update(user_uid):
    """
    Read user from db by user_uid.
    """
    if data := conn.db.users.find_one({"user_uid": user_uid}):
        user = _create_ob(data)
    else:
        user = User({"user_uid": user_uid})

    yield user

    _update(user)


# TODO: remove
def read_status(user_uid, status_uid):
    """
    Read particular user status.
    """
    return conn.db.users.find_one({"user_uid": user_uid, "statuses.status_uid": status_uid})


def create(user):
    """
    Create blank user.

    Actually just a helper function.
    """
    conn.db.users.insert_one(user.to_native())


def update_status(user_uid, points):
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


def read_one(user_uid):
    """
    Read user/game_profile from db.
    """
    return _create_ob(conn.db.users.find_one({"user_uid": user_uid}) or {"user_uid": user_uid})


def update_badge(user_uid, badge_uid, badge_url, progress, done, upsert):
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

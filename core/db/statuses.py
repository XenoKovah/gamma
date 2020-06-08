from schematics.exceptions import DataError

from core.data_models.models import Status
from core.db.engine import conn


def _create_status(data) -> Status:
    try:
        status = Status().import_data(data)
    except DataError:
        status = None
    return status


def read():
    """
    Read all system statuses.
    """
    return [_create_status(status) for
        status in conn.db.statuses.find({"active": True})]


def read_one(status_uid):
    """
    Read all user statuses.
    """
    data = conn.db.statuses.find_one({"status_uid": status_uid})
    return _create_status(data)


def update(status):
    """
    Update/upsert status badge.

    status: Status model
    """
    conn.db.statuses.update_one(
        {"status_uid": status.status_uid},
        {"$set": status.to_native()},
        upsert=True
    )

def get_achieved(prev_points, new_points):
    """
    Return top status that can be achieved between two points.

    Return None if specified status does not exist.
    """
    res = list(
        conn.db.statuses.find(
            {"active": True, "status_points": {"$gt": prev_points, "$lte": new_points}}
        ).sort([("status_points", -1)]).limit(1))
    return res[0]['status_uid'] if res else None

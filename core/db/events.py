import logging

from pymongo import WriteConcern
from schematics.exceptions import DataError

from core.data_models.models import SystemEvent
from core.db.engine import conn


LOG = logging.getLogger(__name__)


def _create_ob(data) -> SystemEvent:
    try:
        system_event = SystemEvent(data, strict=False)
    except DataError as ex:
        system_event = None
        LOG.error(f"Can't import SystemEvent data {ex}")  # pylint: disable=logging-fstring-interpolation
    return system_event


def log(event):
    """
    Check event before saving.

    Return None in case of duplicated event.
    """
    event.validate()

    if conn.db.event_history.find_one({"uid": event.uid, "user_uid": event.username, "client": event.client}):
        return None

    conn.db.event_history.with_options(write_concern=WriteConcern(w=0)).insert_one(event.to_native())

    return event


def read():
    """
    Read all accepted events.
    """
    return [_create_ob(event) for event in conn.db.events.find()]


def read_one(event_type):
    """
    Read system event.
    """
    event = {}
    if data := conn.db.events.find_one({"event_type": event_type}):
        event = _create_ob(data)
    return event


def update(system_event):
    """
    Update event.

    system_event: SystemEvent
    """
    data = system_event.to_native()
    data.pop("_id")

    conn.db.events.update_one(
        {"event_type": system_event.event_type},
        {"$set": data},
        upsert=True
    )

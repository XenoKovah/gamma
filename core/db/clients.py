import logging

from schematics.exceptions import DataError

from core.data_models.models import AppClient
from core.db.engine import conn


LOG = logging.getLogger(__name__)


def _create_ob(data) -> AppClient:
    try:
        app_client = AppClient(data)
    except DataError as ex:
        LOG.error(f"Can't import AppClient data {ex}")  # pylint: disable=logging-fstring-interpolation
        app_client = None
    return app_client


def update_one(app_client):
    """
    Update AppClient model.
    """
    app_client.validate()

    conn.db.app_clients.update_one(
        {"uid": app_client.uid},
        {"$set": app_client.to_native('internal')},
        upsert=True)


def read_one(key, secret) -> AppClient:
    """
    Read one AppClient.

    Return AppClient object.
    """
    data = conn.db.app_clients.find_one({"key": key, "secret": secret})
    return _create_ob(data)

from schematics.exceptions import DataError

from core.data_models.models import AppClient
from core.db.engine import conn


def _create_ob(data) -> AppClient:
    try:
        app_client = AppClient().import_data(data)
    except DataError:
        app_client = None
    return app_client


def update_one(app_client):
    """
    Update AppClient model.
    """
    conn.db.app_clients.update_one(
        {"uid": app_client.uid},
        {"$set": app_client.to_native('internal')},
        upsert=True)


def read_one(key, secret):
    data = conn.db.app_clients.find_one({"key": key, "secret": secret})
    return _create_ob(data)

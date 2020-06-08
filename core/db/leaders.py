from pymongo import DESCENDING

from core.data_models.models import Leaders
from core.db.engine import conn


def read():
    """
    Read top 100 users based on points field.
    """
    return Leaders().import_data({"roster": conn.db.users.find({}).sort([("points", DESCENDING)]).limit(100)})

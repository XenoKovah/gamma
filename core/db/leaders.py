from pymongo import DESCENDING

from core.data_models.models import Leaders
from core.db.engine import conn


def read():
    """
    Read top 100 users based on points field.
    """
    return Leaders(
        {"roster": conn.db.users.find({}).sort([("points", DESCENDING)]).limit(100)})


def read_with_signup_source(user_signup_source):
    """
    Read the top 100 users of a specific site based on the score field.
    """
    return Leaders(
        {
            "roster": conn.db.users.find({"signup_source": f"{user_signup_source}"}).
                sort([("points", DESCENDING)]).limit(100)
        }
    )


def read_with_main_signup_source():
    """
    Read the top 100 users of the main site and users 
    without signup_source based on the score field.
    """
    return Leaders(
        {
            "roster": conn.db.users.find({
                "$or": [
                    {"signup_source": {"$exists": False}},
                    {"signup_source": None},
                    {"signup_source": "main"}
                ]
            }).sort([("points", DESCENDING)]).limit(100)
        }
    )

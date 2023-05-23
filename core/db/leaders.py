from pymongo import ASCENDING, DESCENDING

from core.data_models.models import Leaders
from core.db.engine import conn
from core import db


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
            "roster": conn.db.users.find(
                {"signup_source": f"{user_signup_source}"}
            ).sort([("points", DESCENDING)]).limit(100)
        }
    )


def read_with_main_signup_source():
    """
    Read the top 100 users of the main site and users without signup_source based on the score field.
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

def get_tenant_filter(user_signup_source):
    if user_signup_source in ("main", None):
        return {
            "$or": [
                {"signup_source": {"$exists": False}},
                {"signup_source": None},
                {"signup_source": "main"}
            ]
        }
    else:
        return {"signup_source": f"{user_signup_source}"}
    

def read_for_user(user_uid, user_signup_source=None):
    """
    Read personalized leaderboard.

    Returns:
        top10: Top 10 users.
        competitors: 
            - 4 users before and 2 users after current user,
            when the user is not in the top 10 and does not occupy the last 2 positions.
            - 5 users before and 1 users after current user,
            when the user possesses the second to last position in the rating.
            - 6 users before and 0 users after current user,
            when the user possesses to last position in the leaderboard, but he has points.
            - an empty list if the user has no points, or the user is in the top 10.
        rank: Current user rank.
    """
    user = db.users.read_one(user_uid)
    _additional_filter = get_tenant_filter(user_signup_source)

    rank = conn.db.users.find({
            "points": {"$gte": user.points}, **_additional_filter
        }).count() if user else None

    top10 = Leaders(
        {
            "roster": conn.db.users.find(_additional_filter)
                .sort([("points", DESCENDING)])
                .limit(10)
        }
    )
    competitors = []
    if user.points == 0:
        rank = None
        return top10, competitors, rank

    if rank > 10:
        # Do not filter it in DB ({"user_uid": {"$ne": user_uid}}) due
        # to performance degradation up to 150ms for each request on
        # 100_000 users.
        tail = list(
            conn.db.users
            .find(
                {"points": {"$lt": user.points}, **_additional_filter})
            .sort([("points", DESCENDING)])
            .limit(2))
        
        if tail == []:
            # the user is last in the ranking but has points
            head_limit = 7
        elif len(tail) == 1:
            # the user is the penultimate in the rating
            head_limit = 6
        else:
            # there are 4 competitors in front of the user, there are 2 competitors behind the user
            head_limit = 5

        head = list(conn.db.users
                                .find({"points": {"$gte": user.points}, **_additional_filter})
                                .sort([("points", ASCENDING)]).limit(head_limit))
        head.reverse()
        head = [user for user in head if user["user_uid"] != user_uid]
        competitors = Leaders({"roster": head + [ user ] + tail})

    return top10, competitors, rank

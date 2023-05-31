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


def get_top10(current_user, rank, additional_filter):
    if rank > 10:
        return Leaders({
            "roster": conn.db.users
                                .find(additional_filter)
                                .sort([("points", DESCENDING)])
                                .limit(10)
        })

    head_top10 = list(
        conn.db.users.find({
            "points": {"$gt": current_user.points},
            **additional_filter
        })
        .sort([("points", DESCENDING)])
        .limit(10)
    )

    if current_user.points == 0:
        return Leaders({"roster": head_top10})

    head_top10_length = len(head_top10)
    if head_top10_length == 9:
        return Leaders({"roster": head_top10 + [ current_user ]})

    tail_top10 = list(
        conn.db.users.find({
            "points": {"$lte": current_user.points},
            **additional_filter
        })
        .sort([("points", DESCENDING)])
        .limit(10 - head_top10_length)
    )
    # TODO this cycle can be removed in the future by
    # adding -> "user_uid": {"$ne": current_user.user_uid} to the query (find block)
    # but preliminary it is necessary to conduct an investigation with big data
    tail_top10 = [user for user in tail_top10 if user["user_uid"] != current_user.user_uid]

    return Leaders({"roster": (head_top10 + [ current_user ] + tail_top10)[:10]})


def get_user_rank(user, additional_filter):
    """
    Determining the current position of the user based on number of points.

    In case of a tie in points with other users, the current user always ranks higher.
    """
    rank_before_current_user = conn.db.users.find({
        "points": {"$gt": user.points}, **additional_filter}).count()
    return rank_before_current_user + 1


def get_tail_competitors(current_user, additional_filter):
    tail = list(
        conn.db.users.find({
            "points": {"$lte": current_user.points},
            **additional_filter
        })
        .sort([("points", DESCENDING)])
        .limit(3)
    )
    # TODO same as in get_top10 -> "user_uid": {"$ne": current_user.user_uid}
    return [user for user in tail if user["user_uid"] != current_user.user_uid][:2]


def get_head_competitors(current_user, head_limit, additional_filter):
    return list(
        conn.db.users
            .find({"points": {"$gt": current_user.points}, **additional_filter})
            .sort([("points", ASCENDING)])
            .limit(head_limit)
    )


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
    additional_filter = get_tenant_filter(user_signup_source)
    rank = get_user_rank(user, additional_filter)
    top10 = get_top10(user, rank, additional_filter)

    competitors = []
    if user.points == 0:
        rank = None
        return top10, competitors, rank

    if rank > 10:
        # Do not filter it in DB ({"user_uid": {"$ne": user_uid}}) due
        # to performance degradation up to 150ms for each request on
        # 100_000 users.
        tail = get_tail_competitors(user, additional_filter)

        # Set a limit on the database query to retrieve users, higher in rating than the current user
        head_limit = 6 - len(tail)

        head = get_head_competitors(user, head_limit, additional_filter)
        head.reverse()
        competitors = Leaders({"roster": head + [ user ] + tail})

    return top10, competitors, rank

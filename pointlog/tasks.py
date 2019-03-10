from __future__ import absolute_import

from django.db.models import Avg, Sum
from django.contrib.auth.models import User

from .models import LoggedEvent

from gamma.celery import app
from achievements.models import Achievement, UserAchievement
from achievements.services import AchievementRulesMongo
from datetime import datetime


AGGREGATIONS = {
    'sum': Sum,
    'avg': Avg
}


@app.task
def check_user_achievements(user_id, log_event):
    """
    Check user achievement by event type.

    Task should be delayed for 30 seconds.
    Called on incoming request for particular event type.
    """
    conn = AchievementRulesMongo()
    conn.connect()
    user = User.objects.get(id=user_id)
    rules_set = conn.collection.find({"rules.actions.{}".format(log_event.event_type): {"$exists": True}})

    results = []
    for rules in rules_set:
        conn.collection.update(
            {"_id": rules["_id"]},
            {
                "$inc": {"rules.{}.{}.count".format(user.id, log_event.event_type): 1},
                "$set": {"rules.{}.{}.last".format(user.id, log_event.event_type): datetime.now()}
            },
            upsert=True
        )
    return results


@app.task
def assign_status(user_id, points):
    """
    Check for status updation.
    """
    user = User.objects.get(id=user_id)
    qs = Achievement.objects.filter(status_badge=True, status_points__lte=points)
    results = []
    for achievement in qs:
        _, created = UserAchievement.objects.get_or_create(
           user=user, achievement=achievement
        )
        msg = (
            'Assigned badge {}'.format(achievement.title) if created else
            'Already exists badge {}'.format(achievement.title)
        )
        results.append(msg)
    return results

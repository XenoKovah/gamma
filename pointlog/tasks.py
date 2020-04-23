from __future__ import absolute_import

from datetime import timedelta, datetime
import pytz

utc=pytz.UTC


from django.db.models import Avg, Sum
from django.contrib.auth.models import User

from .models import LoggedEvent

from gamma.celery import app
from achievements.models import Achievement, UserAchievement, StatusBadge, UserStatus
from achievements.services import AchievementRulesMongo


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
    rules_set = conn.collection.find(
        {
            "rules.actions.{}".format(log_event.event_type): {"$exists": True},
            "active": True
        }
    )

    results = []
    for rules in rules_set:
        if rules.get('users', {}).get(str(user.id), {}).get('done'):
            continue

        filter_set = [getattr(log_event.event_type, key, '') == value for key, value in
                      rules.get('rules', {}).get('filters', {}).items() if getattr(log_event.event_type, key, '')]

        filters = rules.get('rules', {}).get('filters', {})
        frequency = filters.get('frequency', None)
        interval = filters.get('interval', None)
        organization =  filters.get('org', None)

        if frequency:
            try:
                delta = timedelta(frequency)
                document = conn.collection.find_one({"_id": rules["_id"]})
                last = document.get('users', {}).get(str(user.id), {}).get(log_event.event_type, {}).get('last')
                if datetime.now() - last > delta:
                    continue
            except Exception:
                pass
        if interval:
            if not (utc.localize(interval.get('start')) <= log_event.date <= utc.localize(interval.get('end'))):
                continue
        if organization:
            if log_event.org != organization:
                continue

        if not filter_set or all(filter_set):
            conn.collection.update(
                {
                    "_id": rules["_id"]
                },
                {
                    "$inc": {"users.{}.{}.count".format(user.id, log_event.event_type): 1},
                    "$set": {
                        "users.{}.{}.last".format(user.id, log_event.event_type): datetime.now(),
                        # TODO change the logic when we update goal
                        "users.{}.{}.goal".format(
                            user.id, log_event.event_type): rules.get(
                                'rules', {}).get('actions', {}).get(log_event.event_type)
                    }
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
    qs = StatusBadge.objects.filter(status_points__lte=points)
    results = []
    for status in qs:
        _, created = UserStatus.objects.get_or_create(
           user=user, status=status
        )
        msg = (
            'Assigned badge {}'.format(status.title) if created else
            'Already exists badge {}'.format(status.title)
        )
        results.append(msg)
    return results

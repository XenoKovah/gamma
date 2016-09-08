from __future__ import absolute_import

from django.db.models import Avg, Sum
from django.contrib.auth.models import User

from gamma.celery import app
from .models import LoggedEvent
from achievements.models import Achievement, UserAchievement
from achievements.services import AchievementRulesMongo


AGGREGATIONS = {
    'sum': Sum,
    'avg': Avg
}


@app.task
def check_user_achievements(user_id, event_type):
    """
    Check user achievement by event type.

    Task should be delayed for 30 seconds.
    Called on incoming request for particular event type.
    """
    connector = AchievementRulesMongo()
    user = User.objects.get(id=user_id)
    achievement_slug_set = Achievement.objects.filter(
        badge_type=event_type
    ).values_list('slug')
    rules_set = (
        (slug[0], connector.get_rule(achievement_slug=slug[0]))
        for slug in achievement_slug_set
    )

    log_model_fields = [field.name for field in LoggedEvent._meta.fields]
    results = []
    for slug, rules in rules_set:
        qs = LoggedEvent.objects.filter(user=user, event_type=event_type)
        count = rules.get('count')
        if count:
            del rules['count']
        else:
            count = 10

        # Agregations is not used now
        # TODO need to improve aggregation logic
        aggregators = []
        for key, value in rules.items():
            if key in AGGREGATIONS:
                aggregators.append((key, value))
                del rules[key]
            elif key not in log_model_fields:
                del rules[key]

        if rules:
            qs = qs.filter(**rules)

        result = qs.count()
        if result >= count:
            achievement = Achievement.objects.get(slug=slug)
            _, created = UserAchievement.objects.get_or_create(
               user=user, achievement=achievement
            )
            msg = (
                'Assigned for slug: {}'.format(slug) if created else
                'Already exists for slug: {}'.format(slug)
            )
        else:
            msg = 'Not assigned slug: {}'.format(slug)
        results.append(msg)

    return results

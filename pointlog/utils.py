from datetime import timedelta, datetime
import logging
import pytz

from django.db.models import Avg, Sum

from achievements.models import StatusBadge, UserStatus
from achievements.services import AchievementRulesMongo
from core.mongo import c_badges
from core.services import MongoConnector


utc = pytz.UTC
logger = logging.getLogger('events')
STRPTIME_FORMATTER = '%Y-%m-%dT%H:%M:%S.%fZ'

AGGREGATIONS = {
    'sum': Sum,
    'avg': Avg
}


def update_user_status(user_id, points):
    """
    Check for status updation.
    """
    qs = StatusBadge.objects.filter(status_points__lte=points)
    results = []
    for status in qs:
        _, created = UserStatus.objects.get_or_create(
            user_id=user_id, status=status
        )
        msg = (
            'Assigned badge {}'.format(status.title) if created else
            'Already exists badge {}'.format(status.title)
        )
        results.append(msg)
    return results


def update_user_statistics(username, event_type, event_award):
    conn = MongoConnector()
    conn.find_one_and_update(
        filter_dict={
            'date': datetime.strptime(
                str(datetime.now().date()), '%Y-%m-%d'
            ),
            'username': username
        },
        key='points',
        value=event_award
    )
    # TODO refactor this
    conn.find_one_and_update(
        filter_dict={
            'username': username
        },
        key=event_type,
        value=event_award,
        event_type='chart'
    )


def is_badge_granted(user_id, rules, progress, badges_got):
    action_rules = rules.get("actions", {})
    status_badge_rule = rules.get("status_badge")  # could be only one
    badge_rules = rules.get("badges", [])

    try:
        for action in action_rules:
            if progress.get(action, {}).get('count', 0) < action_rules[action]:
                return False

        if status_badge_rule and not UserStatus.objects.filter(
                user_id=user_id, status__slug=status_badge_rule).exists():
            return False

        if badge_rules:
            for badge in badge_rules:
                if badge not in badges_got:
                    return False
    except Exception as e:
        logger.warning("Exception on checking badges rules: {}\n"
                       "Rules data: {}\n"
                       "User data: {}\n".format(e, rules, progress))
        return False

    return True


def update_user_badges_by_event(user_id, event_data):
    event_type = event_data.get('event_type')
    event_date = event_data.get('date')
    event_org = event_data.get('org')
    event_course_id = event_data.get('course_id')

    conn = AchievementRulesMongo()
    conn.connect()
    affected_badges = conn.collection.find({
        "active": True,
        "rules.actions.{}".format(event_type): {"$exists": True}
    })
    user_badges = (c_badges().find_one({"user_id": user_id}, {"_id": 0}) or {}).get('badges', {})
    badges_got = [b for b in user_badges if user_badges[b].get('done')]
    new_badges_granted = []

    for badge in affected_badges:
        badge_slug = badge.get("slug")
        if not user_badges.get(badge_slug, {}).get('done'):
            rules = badge.get("rules", {})
            progress = user_badges.get(badge_slug, {}).get('progress', {})

            filters = rules.get('filters', {})
            frequency = filters.get('frequency', None)
            interval = filters.get('interval', None)
            organization =  filters.get('org', None)
            course_id = filters.get('course', None)

            if frequency:
                # frequency is count of days that should be
                delta = timedelta(frequency)
                last = progress.get('last')
                if last and datetime.now() - last > delta:
                    continue

            if (
                interval and
                interval.get('start') and
                interval.get('end') and not
                (datetime.strptime(interval.get('start'), STRPTIME_FORMATTER)
                    <= datetime.strptime(event_date, STRPTIME_FORMATTER) <= 
                        datetime.strptime(interval.get('end'), STRPTIME_FORMATTER))):
                continue

            if organization and not (event_org and event_org == organization):
                continue

            if course_id and not (event_course_id and event_course_id == course_id):
                continue

            progress[event_type] = {
                'count': progress.get(event_type, {}).get('count', 0) + 1,
                'last': event_date
            }
            badge_granted = is_badge_granted(user_id, rules, progress, badges_got)

            if badge_granted:
                new_badges_granted.append(badge_slug)
                badges_got.append(badge_slug)
                # progress could contain outdated data if badge rules was changed during badge receiving process
                # so update it to actual rules and 'freeze' from further changes
                actions = rules.get('actions', {})
                progress = {event: {'count': actions[event], 'goal': actions[event]} for event in actions}

            c_badges().update(
                {"user_id": user_id},
                {
                    "$set": {
                        "badges.{}.progress".format(badge_slug): progress,
                        "badges.{}.done".format(badge_slug): badge_granted,
                        "badges.{}.url".format(badge_slug): badge.get("url")
                    }
                },
                upsert=True
            )

    return new_badges_granted


def update_badges_by_badges(user_id, badges_granted):
    conn = AchievementRulesMongo()
    conn.connect()
    badges = conn.collection.find({"active": True})
    badges_granted = set(badges_granted)

    new_badges_granted = []

    user_badges = (c_badges().find_one({"user_id": user_id}, {"_id": 0}) or {}).get('badges', {})
    badges_got = [b for b in user_badges if user_badges[b].get('done')]

    for badge in badges:
        required_badges = set(badge.get("rules", {}).get("badges", []))
        badge_slug = badge.get("slug")

        if not user_badges.get(badge_slug, {}).get('done') and required_badges.intersection(badges_granted):
            progress = user_badges.get(badge_slug, {}).get('progress', {})
            badge_granted = is_badge_granted(user_id, badge.get("rules", {}), progress, badges_got)
            if badge_granted:
                actions = badge.get("rules", {}).get('actions', {})
                progress = {event: {'count': actions[event], 'goal': actions[event]} for event in actions}
                c_badges().update(
                    {"user_id": user_id},
                    {
                        "$set": {
                            "badges.{}.progress".format(badge_slug): progress,
                            "badges.{}.done".format(badge_slug): True,
                            "badges.{}.url".format(badge_slug): badge.get("url")
                        }
                    },
                    upsert=True
                )
                new_badges_granted.append(badge_slug)
                badges_got.append(badge_slug)

    return new_badges_granted


def is_badge_rules_simplified(new_rules, old_rules):
    new_actions = new_rules.get('actions', {})
    old_actions = old_rules.get('actions', {})
    new_badges = set(new_rules.get('badges', []))
    old_badges = set(old_rules.get('badges', []))
    new_status_badge = new_rules.get('status_badge')
    old_status_badge = old_rules.get('status_badge')

    actions_simplified = False
    if set(new_actions).issubset(set(old_actions)):  # check no new events added
        for event, value in new_actions.items():
            if value > old_actions[event]:
                return False  # count of events to get badge is increased
            elif value < old_actions[event]:
                actions_simplified = True
    else:  # that means new event(s) added
        return False
    if not actions_simplified:
        actions_simplified = len(new_actions) < len(old_actions)

    status_badge_simplified = False
    if new_status_badge and old_status_badge:
        if new_status_badge != old_status_badge:
            new_status_badge_data = StatusBadge.objects.filter(slug=new_status_badge).first()
            old_status_badge_data = StatusBadge.objects.filter(slug=old_status_badge).first()
            # to avoid error if status badge deleted from DB but not from rules
            if new_status_badge_data and old_status_badge_data:
                if new_status_badge_data.status_points > old_status_badge_data.status_points:
                    return False
                elif new_status_badge_data.status_points < old_status_badge_data.status_points:
                    status_badge_simplified = True
            else:  # badge granting for users might need to be recalculated
                status_badge_simplified = True
    else:
        if old_status_badge and not new_status_badge:  # status badge removed
            status_badge_simplified = True
        # if status badge added, it might be already achieved by user
        # so recalculation might be need if other rules simplified

    badges_simplified = old_badges != new_badges and new_badges.issubset(old_badges)
    # if new badge added, it might not make rules more complicated because it's rules might be already achieved
    # we don't check it recurrently, just assume it

    return actions_simplified or status_badge_simplified or badges_simplified

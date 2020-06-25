import logging
from datetime import datetime, timedelta

from core import db


logger = logging.getLogger('events')
STRPTIME_FORMATTER = '%Y-%m-%dT%H:%M:%S.%fZ'


def update_badges_by_badges(user_uid, badges_granted):
    badges = db.badges.read_active()
    badges_granted = set(badges_granted)

    user = db.users.read_one(user_uid)
    user_badges = user.badges
    badges_got = user.achieved_badges

    new_badges_granted = []

    for badge in badges:
        required_badges = set(badge.get("rules", {}).get("badges", []))
        badge_slug = badge.get("slug")

        if not user_badges.get(badge_slug, {}).get('done') and required_badges.intersection(badges_granted):
            progress = user_badges.get(badge_slug, {}).get('progress', {})
            if is_badge_granted(user_uid, badge.get("rules", {}), progress, badges_got):
                actions = badge.get("rules", {}).get('actions', {})
                progress = {event: {'count': actions[event], 'goal': actions[event]} for event in actions}
                db.users.update_badge(user_uid, badge_slug, badge.get("url"),
                                      badge.get("title"), progress, True, True)
                new_badges_granted.append(badge_slug)
                badges_got.append(badge_slug)

    return new_badges_granted


def update_user_badges_by_event(user_uid, event_data, achieved_status_uid):
    event_type = event_data.get('event_type')
    event_date = event_data.get('date')
    event_org = event_data.get('org')
    event_course_id = event_data.get('course_id')

    affected_badges = db.engine.conn.db.badges.find({
        "active": True,
        "$or": [{f"rules.actions.{event_type}": {"$exists": True}},
                {"$and": [{"rules.status_badge": achieved_status_uid}, {"rules.status_badge": {"$exists": True}}]}]
    })

    user = db.users.read_one(user_uid)
    user_badges = user.to_native().get("badges")
    badges_got = user.achieved_badges

    new_badges_granted = []

    for badge in affected_badges:
        badge_slug = badge.get("slug")
        if not user_badges.get(badge_slug, {}).get('done'):
            rules = badge.get("rules", {})
            progress = user_badges.get(badge_slug, {}).get('progress', {})

            filters = rules.get('filters', {})
            frequency = filters.get('frequency', None)
            interval = filters.get('interval', None)
            organization = filters.get('org', None)
            course_id = filters.get('course', None)
            is_affected_by_event = event_type in rules.get('actions', {})

            if is_affected_by_event:
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
                    interval.get('start')
                        <= datetime.strptime(event_date, STRPTIME_FORMATTER) <=
                            interval.get('end')):
                    continue

                if organization and not (event_org and event_org == organization):
                    continue

                if course_id and not (event_course_id and event_course_id == course_id):
                    continue

                progress[event_type] = {
                    'count': progress.get(event_type, {}).get('count', 0) + 1,
                    'last': event_date
                }

            badge_granted = is_badge_granted(user_uid, rules, progress, badges_got)

            if badge_granted:
                new_badges_granted.append(badge_slug)
                badges_got.append(badge_slug)
                # progress could contain outdated data if badge rules was changed during badge receiving process
                # so update it to actual rules and 'freeze' from further changes
                actions = rules.get('actions', {})
                progress = {event: {'count': actions[event], 'goal': actions[event]} for event in actions}
                # TODO: save badges and status dependencies for granted badges
                # to output it if granted badge is deactivated

            if is_affected_by_event or badge_granted:
                db.users.update_badge(user_uid, badge_slug, badge.get("url"),
                                      badge.get("title"), progress, badge_granted, True)

    return new_badges_granted


def is_badge_granted(user_uid, rules, progress, badges_got):
    action_rules = rules.get("actions", {})
    status_badge_rule = rules.get("status_badge")  # could be only one
    badge_rules = rules.get("badges", [])

    try:
        for action in action_rules:
            if progress.get(action, {}).get('count', 0) < action_rules[action]:
                return False

        if status_badge_rule and not db.users.read_status(user_uid, status_badge_rule):
            return False

        if badge_rules:
            for badge in badge_rules:
                if badge not in badges_got:
                    return False
    except Exception as ex:
        logger.warning(f"Exception on checking badges rules: {ex}\n"
                       f"Rules data: {rules}\n"
                       f"User data: {progress}\n")
        return False

    return True


def is_badge_rules_simplified(new_rules, old_rules) -> bool:
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
            new_status_badge_data = db.statuses.read_one(new_status_badge)
            old_status_badge_data = db.statuses.read_one(old_status_badge)
            # to avoid error if status badge deleted from DB but not from rules
            if new_status_badge_data and old_status_badge_data:
                if new_status_badge_data > old_status_badge_data:
                    return False
                elif new_status_badge_data < old_status_badge_data:
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


class AppClientUtils:
    """
    Misc utility method to work with AppClient.
    """
    _app_client = None

    def get_app_client(self, request):
        key = request.META.get('HTTP_APP_KEY')
        secret = request.META.get('HTTP_APP_SECRET')

        if not self._app_client:
            self._app_client = db.clients.read_one(key, secret)

        return self._app_client

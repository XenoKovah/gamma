import logging
from typing import Set
from datetime import datetime, timedelta

from core.data_models.models import UserAction, UserBadge, Rules
from core import db


logger = logging.getLogger('events')
STRPTIME_FORMATTER = '%Y-%m-%dT%H:%M:%S.%fZ'


def update_badges_by_badges(user_uid, badges_granted):
    """
    Update badges by a granted ones.

    Find all affected badges by iteration over active system badges
    and compare Badge.required_badges (Badge.rules.badges) rule
    with User.badges.
    """
    badges = db.badges.read_active()
    user = db.users.read_one(user_uid)

    # dinamic list created from User.badges field
    badges_got = user.achieved_badges

    new_badges_granted = []

    for badge in badges:

        if not user.badges.get(badge.badge_uid, {}).get('done') and \
                set(badge.required_badges).intersection(badges_granted):

            progress = user.badges.get(badge.badge_uid, {}).get('progress', {})
            if badge.rules and is_badge_granted(user, badge.rules, progress):
                """
                Changing progress to
                {
                  'count': action_goal,
                  'goal': action_goal
                }
                """
                with db.users.read_and_update(user.user_uid) as user:

                    actions = badge.rules.actions
                    progress = {
                        event: UserAction({
                            # in case this badge has no action in rules
                            'count': actions.get(event, 0),
                            'goal': actions.get(event, 0)
                        }) for event in actions
                    }
                    user_badge = UserBadge({
                        "title": badge.title,
                        "description": badge.description,
                        "url": badge.url,
                        "done": True,
                        "progress": progress
                    })
                    user.badges[badge.badge_uid] = user_badge

                new_badges_granted.append(badge.badge_uid)
                badges_got.append(badge.badge_uid)

    return new_badges_granted


def update_user_badges_by_event(user_uid, event, achieved_status_uid):
    """
    Pass event through filtering.

    Also take into account newly achieved status.
    """
    _filter = {
        "active": True,
        "$or": [{f"rules.actions.{event.event_type}": {"$exists": True}},
                {"$and": [
                    {"rules.status_badge": achieved_status_uid},
                    {"rules.status_badge": {"$exists": True}}]}]}

    affected_badges = db.badges.read(_filter)

    user = db.users.read_one(user_uid)
    badges_got = user.achieved_badges

    new_badges_granted = []

    for badge in affected_badges:
        if not user.badges.get(badge.badge_uid, {}).get('done'):
            progress = user.badges.get(badge.badge_uid, {}).get('progress', {})

            is_affected_by_event = event.event_type in badge.rules.actions if badge.rules else False

            if is_affected_by_event and filter_event(event, badge.rules.filters, progress):

                if not check_frequency_fit(badge.rules.filters, progress, event):
                    # if frequency condition is not performed and count don't reach goal value
                    # it triggers progress recalculation for the current event
                    # and set it's value to 1
                    if progress.get(event.event_type, {}).get('count', 0) < badge.rules.actions[event.event_type]:
                        progress[event.event_type] = UserAction({'count': 1, 'last': event.date})
                else:
                    # TODO: refactor this to use atomic Mongo $inc
                    progress[event.event_type] = UserAction({
                        'count': progress.get(event.event_type, {}).get('count', 0) + 1,
                        'last': event.date})

            if badge.rules and (badge_granted := is_badge_granted(user, badge.rules, progress)):
                """
                Changing progress to
                {
                  'count': action_goal,
                  'goal': action_goal
                }
                """
                new_badges_granted.append(badge.badge_uid)
                badges_got.append(badge.badge_uid)
                # progress could contain outdated data if badge rules was changed during badge receiving process
                # so update it to actual rules and 'freeze' from further changes
                actions = badge.rules.actions
                progress = {
                    event: UserAction({
                        # in case this badge has no action in rules
                        'count': actions.get(event, 0),
                        'goal': actions.get(event, 0),
                    }) for event in actions
                }
                # TODO: save badges and status dependencies for granted badges
                # to output it if granted badge is deactivated

            if is_affected_by_event or badge_granted:
                # TODO: optimize to write once all collected updates
                with db.users.read_and_update(user.user_uid) as user:
                    user_badge = UserBadge({
                        "title": badge.title,
                        "description": badge.description,
                        "url": badge.url,
                        "done": badge_granted,
                        "progress": progress
                    })
                    user.badges[badge.badge_uid] = user_badge

    return new_badges_granted


def filter_event(event, filters, progress):
    """
    Filter Event by a given rules.

    Return True if event does pass the filtering.
    Return False if event doesn't pass the filtering.
    """
    if not filters: return True

    if (filters.interval and
            filters.interval.start and
            filters.interval.end and not
            (filters.interval.start <= event.date <= filters.interval.end)):

        return False

    if filters.org and not (event.org and event.org == filters.org):
        return False

    if filters.course and not (event.course_id and event.course_id == filters.course):
        return False

    return True


def check_frequency_fit(filters, progress, event):
    """
    Check if frequency rule is performed for the event.

    Frequency is count of days between same type events,
    i.e. Frequency 2 means that if some type of event for badge is not
    performed during 2 days, badge progress for the event should be reset
    to 1 when new event of this type is received.
    Other events from rules won't be affected.
    """
    if not filters: return True

    if filters.frequency:
        delta = timedelta(filters.frequency)
        last = progress.get(event.event_type, {}).get('last')

        if last and event.date - last > delta:
            return False

    return True


def is_badge_granted(user, rules: Rules, progress):
    """
    Check for all badge rules to be passed.
    """
    if not rules: return False

    for action in rules.actions:
        if progress.get(action, {}).get('count', 0) < rules.actions[action]:
            return False

    if rules.status_badge and not user.has_status(rules.status_badge):
        return False

    for badge in rules.badges:
        if badge not in user.achieved_badges:
            return False

    return True


def is_badge_rules_simplified(new_rules: Rules, old_rules: Rules) -> bool:
    """
    Check where the changed rules simplify constraints.
    """
    if not new_rules: return False

    new_badges_set = set(new_rules.badges)
    old_badges_set = set(old_rules.badges)

    actions_simplified = False
    status_badge_simplified = False

    # check no new events added
    if not set(new_rules.actions).issubset(set(old_rules.actions)):
        return False

    for event, value in new_rules.actions.items():
        if value > old_rules.actions[event]:
            return False  # count of events to get badge is increased
        elif value < old_rules.actions[event]:
            actions_simplified = True

    if not actions_simplified:
        actions_simplified = len(new_rules.actions) < len(old_rules.actions)

    # Status badge simplification check
    if (new_rules.status_badge and old_rules.status_badge and (new_rules.status_badge != old_rules.status_badge) and
            not (status_badge_simplified := is_status_simplified(new_rules.status_badge, old_rules.status_badge))):
        return False

    # if status badge added, it might be already achieved by user
    # so recalculation might be need if other rules simplified
    elif old_rules.status_badge and not new_rules.status_badge:  # status badge removed
        status_badge_simplified = True

    return actions_simplified or status_badge_simplified or is_badge_simplified(old_badges_set, new_badges_set)


def is_badge_simplified(old_badges_set: Set[Rules], new_badges_set: Set[Rules]) -> bool:
    """
    Badge dependency simplification check.

    If new badge added, it might not make rules more complicated because
    it's rules might be already achieved
    we don't check it recurrently, just assume it.
    """
    return old_badges_set != new_badges_set


def is_status_simplified(new_status_badge, old_status_badge):
    """
    Check new status for simplification.
    """
    status_badge_simplified = False

    new_status_badge_data = db.statuses.read_one(new_status_badge)
    old_status_badge_data = db.statuses.read_one(old_status_badge)

    # to avoid error if status badge deleted from DB but not from rules
    if new_status_badge_data and old_status_badge_data:
        if new_status_badge_data > old_status_badge_data:
            status_badge_simplified = False
        elif new_status_badge_data < old_status_badge_data:
            status_badge_simplified = True

    else:  # badge granting for users might need to be recalculated
        status_badge_simplified = True

    return status_badge_simplified


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


def clean_rules(data):
    cleaned_rules = {}
    for key, value in data.items():
        if key in Rules._schema.fields:
            cleaned_rules[key] = value

    return cleaned_rules

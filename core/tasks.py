import logging
from django.conf import settings
from gamma.celery import app

from core.utils import (
    is_badge_rules_simplified,
    update_badges_by_badges,
    update_user_badges_by_event,
    is_badge_granted
)
from core import db
from core import onesignal_provider
from core.data_models.models import UserAction, UserBadge, Rules, EventModel

log = logging.getLogger(__name__)


@app.task
def update_user_position(user_uid, points, event_data):
    # update_user_status should be run before updating user badges
    db.users.update_status(user_uid, points)
    event = EventModel(event_data)

    prev_points = points - event.points
    if achieved_status_uid := db.statuses.get_achieved(prev_points, points):
        notify_status_granted.delay(user_uid, achieved_status_uid)

    if badges_granted := update_user_badges_by_event(user_uid, event, achieved_status_uid):
        notify_badges_granted.delay(user_uid, badges_granted)
        # for resolving badge-for-badges achievements
        # TODO: rewrite this to be able to grant when dependency already achieved
        # TODO: handle case when dependend badge was granted before dependency was intoduced
        while badges_granted := update_badges_by_badges(user_uid, badges_granted):
            notify_badges_granted.delay(user_uid, badges_granted)


@app.task
def notify_badges_granted(user_uid, badges):
    user = db.users.read_one(user_uid)
    for badge_slug in badges:
        badge = db.badges.read_one(badge_slug)
        data = {
            "head": "New Achievement!",
            "body": badge.title,
            "lang": "en",
            "icon": badge.url,
            "url":  f"{settings.EDX_LMS_BASE_URL}/dashboard/gamification/"
        }
        try:
            onesignal_provider.send_notif(user, data)
        except Exception as ex:
            log.debug(ex)


@app.task
def notify_status_granted(user_uid, status_uid):
    user = db.users.read_one(user_uid)
    status = db.statuses.read_one(status_uid)
    data = {
        "head": "New Status!",
        "body": status.title,
        "lang": "en",
        "icon": status.url,
        "url": f"{settings.EDX_LMS_BASE_URL}/dashboard/gamification/"
    }
    try:
        onesignal_provider.send_notif(user, data)
    except Exception as ex:
        log.debug(ex)


@app.task
def update_users_badge_data(badge_slug, old_rules, new_rules, badge_url, badge_title):
    """
    Run on badge rules change, recalculate badges granted for users if needed.
    """
    old_rules = Rules(old_rules)
    new_rules = Rules(new_rules)

    if not is_badge_rules_simplified(new_rules, old_rules):
        return

     # if no actions, users without data for the badge could be affected
    _filter = {
        f"badges.{badge_slug}.done": False if new_rules.get('actions') else {'$ne': True}
    }

    for user in db.users.read(_filter):

        user_progress = user.badges.get(badge_slug, {}).get('progress', {})
        if is_badge_granted(user, new_rules, user_progress):
            """
            Changing progress to
            {
              'count': action_goal,
              'goal': action_goal
            }
            """
            with db.users.read_and_update(user.user_uid) as user:

                actions = new_rules.get('actions', {})
                progress = {
                    event: UserAction({
                        # in case this badge has no action in rules
                        'count': actions.get(event, 0),
                        'goal': actions.get(event, 0)
                    }) for event in actions
                }
                user_badge = UserBadge({
                    "title": badge_title,
                    "url": badge_url,
                    "done": True,
                    "progress": progress
                })
                user.badges[badge_slug] = user_badge

            badges_granted = [badge_slug]
            notify_badges_granted.delay(user.user_uid, badges_granted)

            while badges_granted:
                if badges_granted := update_badges_by_badges(user.user_uid, badges_granted):
                    notify_badges_granted.delay(user.user_uid, badges_granted)

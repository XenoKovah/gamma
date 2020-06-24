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

log = logging.getLogger(__name__)


@app.task
def update_user_position(user_uid, points, event_data):
    # update_user_status should be run before updating user badges
    db.users.update_status(user_uid, points)

    prev_points = points - event_data.get('points')
    if achieved_status_uid := db.statuses.get_achieved(prev_points, points):
        # TODO: Invoke badges_by_badges flow
        notify_status_granted.delay(user_uid, achieved_status_uid)

    if badges_granted := update_user_badges_by_event(user_uid, event_data):
        notify_badges_granted.delay(user_uid, badges_granted)
        # for resolving badge-for-badges achievements
        # TODO: rewrite this to be able to grant when dependency already achieved
        # TODO: handle case when dependend badge was granted befoe dependency was intoduced
        while badges_granted := update_badges_by_badges(user_uid, badges_granted):
            notify_badges_granted.delay(user_uid, badges_granted)


@app.task
def notify_badges_granted(user_uid, badges):
    user = db.users.read_one(user_uid)
    for badge_slug in badges:
        badge = db.badges.read_one_as_ob(badge_slug)
        data = {
            "head": "New Achievement!",
            "body": badge.title,
            "lang": "en",
            "icon": badge.url,
            "url":  f"{settings.EDX_LMS_BASE_URL}/dashboard/gamification/"
        }
        try:
            onesignal_provider.send_notif(user, data)
        except Exception as e:
            log.debug(e)


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
    except Exception as e:
        log.debug(e)


@app.task
def update_users_badge_data(badge_slug, old_rules, new_rules, badge_url, badge_title):
    """
    Run on badge rules change, recalculate badges granted for users if needed.
    """
    if not is_badge_rules_simplified(new_rules, old_rules):
        return
    if new_rules.get('actions'):
        users_badges_data = db.engine.conn.db.users.find({'badges.{}.done'.format(badge_slug): False})
    else:
        # if no actions, users without data for the badge could be affected
        users_badges_data = db.engine.conn.db.users.find({'badges.{}.done'.format(badge_slug): {'$ne': True}})
    for user_data in users_badges_data:
        user_uid = user_data.get('user_uid')
        user_badges = user_data.get('badges', {})
        badges_got = [b for b in user_badges.get('progress', {}) if b.get('done')]
        granted = is_badge_granted(
            user_uid,
            new_rules,
            user_badges.get(badge_slug, {}).get('progress', {}),
            badges_got
        )
        if granted:
            actions = new_rules.get('actions', {})
            progress = {event: {'count': actions[event], 'goal': actions[event]} for event in actions}
            db.users.update_badge(user_uid, badge_slug, badge_url, badge_title, progress, True, False)
            badges_granted = [badge_slug]
            while badges_granted:
                badges_granted = update_badges_by_badges(user_uid, badges_granted)

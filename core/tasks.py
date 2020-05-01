from gamma.celery import app

from core.utils import (
    is_badge_rules_simplified,
    update_badges_by_badges,
    update_user_badges_by_event,
    is_badge_granted
)
from core import db


@app.task
def update_user_position(user_uid, game_points, event_data):
    db.update_user_progress(user_uid, event_data.get('points'))
    db.update_charted_progress(user_uid, event_data.get('event_type'), event_data.get('points'))
    # update_user_status should be run before updating user badges
    db.update_user_status(user_uid, game_points)

    if (badges_granted := update_user_badges_by_event(user_uid, event_data)):
        # for resolving badge-for-badges achievements
        # TODO: rewrite this to be able to grant when dependency already achieved
        while (badges_granted := update_badges_by_badges(user_uid, badges_granted)):
            pass


@app.task
def update_users_badge_data(badge_slug, old_rules, new_rules, badge_url):
    """
    Run on badge rules change, recalculate badges granted for users if needed.
    """
    if not is_badge_rules_simplified(new_rules, old_rules):
        return
    if new_rules.get('actions'):
        users_badges_data = db.conn.db.users.find({'badges.{}.done'.format(badge_slug): False})
    else:
        # if no actions, users without data for the badge could be affected
        users_badges_data = db.conn.db.users.find({'badges.{}.done'.format(badge_slug): {'$ne': True}})
    for user_data in users_badges_data:
        user_uid = user_data.get('user_uid')
        user_badges = user_data.get('badges')
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
            db.update_user_badge(user_uid, badge_slug, badge_url, progress, True, False)
            badges_granted = [badge_slug]
            while badges_granted:
                badges_granted = update_badges_by_badges(user_uid, badges_granted)

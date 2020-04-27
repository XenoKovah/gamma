from core.mongo import c_badges
from gamma.celery import app
from pointlog.utils import is_badge_granted, update_user_status, update_user_badges_by_event, \
    update_badges_by_badges, update_user_statistics, is_badge_rules_simplified


@app.task
def update_user_position(user_id, username, game_points, event_type, event_award, event_date, event_org):
    update_user_statistics(username, event_type, event_award)
    # update_user_status should be run before updating user badges
    update_user_status(user_id, game_points)
    badges_granted = update_user_badges_by_event(user_id, event_type, event_date, event_org)
    # for resolving badge-for-badges achievements
    while badges_granted:
        badges_granted = update_badges_by_badges(user_id, badges_granted)


@app.task
def update_users_badge_data(badge_slug, old_rules, new_rules, badge_url):
    # on badge rules rules change, recalculate badges granted for users if needed
    if not is_badge_rules_simplified(new_rules, old_rules):
        return
    if new_rules.get('actions'):
        users_badges_data = c_badges().find({'badges.{}.done'.format(badge_slug): False})
    else:
        # if no actions, users without data for the badge could be affected
        users_badges_data = c_badges().find({'badges.{}.done'.format(badge_slug): {'$ne': True}})
    for user_data in users_badges_data:
        user_id = user_data.get('user_id')
        user_badges = user_data.get('badges')
        badges_got = [b for b in user_badges.get('progress', {}) if b.get('done')]
        granted = is_badge_granted(
            user_id,
            new_rules,
            user_badges.get(badge_slug, {}).get('progress', {}),
            badges_got
        )
        if granted:
            actions = new_rules.get('actions', {})
            progress = {event: {'count': actions[event], 'goal': actions[event]} for event in actions}
            c_badges().update(
                {"user_id": user_id},
                {
                    "$set": {
                        "badges.{}.progress".format(badge_slug): progress,
                        "badges.{}.done".format(badge_slug): True,
                        "badges.{}.url".format(badge_slug): badge_url
                    }
                },
            )
            badges_granted = [badge_slug]
            while badges_granted:
                badges_granted = update_badges_by_badges(user_id, badges_granted)

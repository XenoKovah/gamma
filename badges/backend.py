from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType

from django.db import transaction

from achievements.models import Achievement, AchievementRule
from badges.models import Badge


User = get_user_model()

class BadgeBackend:
    """
    """

    def create_draft_acievement(self, rule, event):
        badges = Badge.objects.filter(rules=rule).prefetch_related('rules')
        
        user = User.objects.get(username=event.username)

        for badge in badges:
            self.draft_acievement_from_badge(badge, user, event)

    @transaction.atomic
    def draft_acievement_from_badge(self, badge, user, event):
        content_type = ContentType.objects.get_for_model(Badge)

        achievement = Achievement.objects.create(
            user=user,
            content_type=content_type,
            object_id=badge.id,
            title=badge.title,
            description=badge.description,
        )
        achivemtents_rules = []

        for rule in badge.rules.all():

            achivemtents_rules.append(
                AchievementRule(
                    achievement=achievement,
                    rule=rule,
                    status=AchievementRule.STATUS_ACTIVE,
                    points=event.points
                )
            )
            
        AchievementRule.objects.bulk_create(achivemtents_rules)

        return

#     def process_event(self, user_uid, event, achieved_status_uid):
#         """"""
#         badges_granted = self.update_user_badges_by_event(user_uid, event, achieved_status_uid)

#         if badges_granted := update_user_badges_by_event(user_uid, event, achieved_status_uid):
#             notify_badges_granted.delay(user_uid, badges_granted)
#             # for resolving badge-for-badges achievements
#             # TODO: rewrite this to be able to grant when dependency already achieved
#             # TODO: handle case when dependend badge was granted before dependency was intoduced
#             while badges_granted := update_badges_by_badges(user_uid, badges_granted):
#                 notify_badges_granted.delay(user_uid, badges_granted)


#     def update_user_badges_by_event(self, user_uid, event, achieved_status_uid):
#         """
#         Pass event through filtering.

#         Also take into account newly achieved status.
#         """
#         _filter = {
#             "active": True,
#             "$or": [{f"rules.actions.{event.event_type}": {"$exists": True}},
#                     {
#                         "$and": [
#                             {"rules.status_badge": achieved_status_uid},
#                             {"rules.status_badge": {"$exists": True}}]}
#                         ]
#                     }

#         affected_badges = db.badges.read(_filter)

#         user = db.users.read_one(user_uid)
#         badges_got = user.achieved_badges

#         new_badges_granted = []

#         for badge in affected_badges:
#             if not user.badges.get(badge.badge_uid, {}).get('done'):
#                 progress = user.badges.get(badge.badge_uid, {}).get('progress', {})

#                 is_affected_by_event = event.event_type in badge.rules.actions if badge.rules else False

#                 if is_affected_by_event and filter_event(event, badge.rules.filters, progress):

#                     if not check_frequency_fit(badge.rules.filters, progress, event):
#                         # if frequency condition is not performed and count don't reach goal value
#                         # it triggers progress recalculation for the current event
#                         # and set it's value to 1
#                         if progress.get(event.event_type, {}).get('count', 0) < badge.rules.actions[event.event_type]:
#                             progress[event.event_type] = UserAction({'count': 1, 'last': event.date})
#                     else:
#                         # TODO: refactor this to use atomic Mongo $inc
#                         progress[event.event_type] = UserAction({
#                             'count': progress.get(event.event_type, {}).get('count', 0) + 1,
#                             'last': event.date})

#                 if badge.rules and (badge_granted := is_badge_granted(user, badge.rules, progress)):
#                     # pylint: disable=pointless-string-statement
#                     """
#                     Changing progress to
#                     {
#                     'count': action_goal,
#                     'goal': action_goal
#                     }
#                     """
#                     new_badges_granted.append(badge.badge_uid)
#                     badges_got.append(badge.badge_uid)
#                     # progress could contain outdated data if badge rules was changed during badge receiving process
#                     # so update it to actual rules and 'freeze' from further changes
#                     actions = badge.rules.actions
#                     progress = {
#                         event: UserAction({
#                             # in case this badge has no action in rules
#                             'count': actions.get(event, 0),
#                             'goal': actions.get(event, 0),
#                         }) for event in actions
#                     }
#                     # TODO: save badges and status dependencies for granted badges
#                     # to output it if granted badge is deactivated

#                 if is_affected_by_event or badge_granted:
#                     # TODO: optimize to write once all collected updates
#                     with db.users.read_and_update(user.user_uid) as user:
#                         user_badge = UserBadge({
#                             "title": badge.title,
#                             "description": badge.description,
#                             "url": badge.url,
#                             "done": badge_granted,
#                             "progress": progress
#                         })
#                         user.badges[badge.badge_uid] = user_badge

#         return new_badges_granted

#     def provide_info(self, user_id):

#         return


# def filter_event(event, filters, progress):
#     """
#     Filter Event by a given rules.

#     Return True if event does pass the filtering.
#     Return False if event doesn't pass the filtering.
#     """
#     if not filters:
#         return True

#     if (filters.interval and
#             filters.interval.start and
#             filters.interval.end and not
#             (filters.interval.start <= event.date <= filters.interval.end)):

#         return False

#     if filters.org and not (event.org and event.org == filters.org):
#         return False

#     if filters.course and not (event.course_id and event.course_id == filters.course):
#         return False

#     return True

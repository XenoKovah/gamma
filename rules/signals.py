from django.db.models.signals import post_save
from django.dispatch import receiver

from events.models import Event
from rules.models import Rule
from achievements.models import AchievementRule
from users.models import GammaUser

from core.utils import get_gamification_backends

# TODO: Should be refactored as part of #NAU-142 Rules refactoring.
# @receiver(post_save, sender=Event)
def process_event_creation(sender, instance, created, **kwargs):
    """
    This signal is triggered when an Event is created.

    The handler processes the event according to the rules defined.
    """
    event = instance

    # Commented for testing locally
    # if not created:
    #     return

    event_type_rules = Rule.objects.prefetch_related('rule_achievements').filter(event_type__name=event.event_type)

    # HERE SHOULD BE LOGIC OF COMPARATION THAT RULE COMPLETED.

    for rule in event_type_rules:
        acievents_to_update = rule.rule_achievements.all()

        if not acievents_to_update:
            for backend in get_gamification_backends():
                backend.create_draft_acievement(rule, event)

        acievents_to_update = rule.rule_achievements.all()
        acievents_to_update.update(status=AchievementRule.STATUS_COMPLETED)

    GammaUser.update_user_progress(event.username, event.points)
    GammaUser.update_user_chart(event.username, event)
    GammaUser.update_user_points(event.username, event.points)

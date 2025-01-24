from django.db.models.signals import post_save
from django.dispatch import receiver

from achievements.models import AchievementRule
from events.models import Event
from core.utils import get_gamification_backends

from .filters import RulesFilter
from .models import Rule


@receiver(post_save, sender=Event)
def process_event_creation(sender, instance, created, **kwargs):
    """
    This signal is triggered when an Event is created.

    The handler processes the event according to the rules defined.
    """

    event = instance
    configuration = event.configuration

    # Commented for testing locally
    # if not created:
    #     return

    affected_rules_by_event = Rule.objects.filter(
        event_configuration=configuration
    ).exclude(
        rule_achievements__status=AchievementRule.Statuses.COMPLETED
    ).prefetch_related('rule_achievements')

    rule_filter = RulesFilter(event)
    affected_rules = rule_filter.filter_rules(affected_rules_by_event)

    for rule in affected_rules:
        achievements_to_update = rule.rule_achievements.all()

        if not achievements_to_update:
            for backend in get_gamification_backends():
                backend.create_draft_achievement(rule, event)

        # acievents_to_update = rule.rule_achievements.all()
        # acievents_to_update.update(status=AchievementRule.STATUS_COMPLETED)

    # GammaUser.update_user_progress(event.username, event.points)
    # GammaUser.update_user_chart(event.username, event)
    # GammaUser.update_user_points(event.username, event.points)

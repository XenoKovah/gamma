from django.db.models.signals import post_save
from django.dispatch import receiver

from achievements.models import AchievementRule
from events.models import Event
from core.utils import get_gamification_backends
from users.models import GammaUser

from .services import RulesFilterService
from .models import Rule


@receiver(post_save, sender=Event)
def process_event_creation(sender, instance, created, **kwargs):
    """
    This signal is triggered when an Event is created.

    The handler processes the event according to the rules defined.
    """

    if not created:
        return

    event = instance
    configuration = event.configuration
    user = GammaUser.ensure_gamma_user_is_created(user_uid=event.username)

    affected_rules_by_event = Rule.objects.filter(
        event_configuration=configuration
    ).exclude(
        rule_achievements__achievement__user=user,
        rule_achievements__status=AchievementRule.Statuses.COMPLETED
    ).prefetch_related('rule_achievements')

    rule_filter = RulesFilterService(event)
    affected_rules = rule_filter.filter_rules(affected_rules_by_event)

    for rule in affected_rules:
        achievements_to_update = rule.rule_achievements.filter(achievement__user=user).all()
        is_achievement_exists = achievements_to_update.exists()

        for backend in get_gamification_backends():
            backend.process_achievement(rule, event, user, is_achievement_exists)

    user.run_update_user_pipeline(configuration)

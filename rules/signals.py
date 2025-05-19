from django.db.models.signals import post_save
from django.dispatch import receiver

from core.utils import get_gamification_backends
from events.models import Event, EventConfiguration
from rules.models import Rule
from rules.services import RulesFilterService
from users.models import GammaUser


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

    affected_rules_by_event = Rule.objects.not_completed_by_user(configuration, user)
    rule_filter = RulesFilterService(event)
    affected_rules = rule_filter.filter_rules(affected_rules_by_event)

    for rule in affected_rules:
        for backend in get_gamification_backends():
            backend.process_achievement(rule, event, user)

    # To avoid recursion we limit the calls only for common events.
    if configuration.event_name in EventConfiguration.common_event_names():
        user.run_update_user_pipeline(event)

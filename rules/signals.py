from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from core.utils import get_gamification_backends
from events.models import Event, EventConfiguration
from rules.models import Rule
from rules.services import RulesFilterService
from users.continuous_learning import register_active_day
from users.models import GammaUser


@receiver(post_save, sender=Event)
def process_event_creation(sender, instance, created, **kwargs):
    """
    This signal is triggered when an Event is created.

    The handler processes the event according to the rules defined.

    All work for a single user is serialized under a row lock on that user. The
    gamification bridge dispatches every Open edX tracking event as its own
    Celery task, and the RGG worker runs them concurrently, so two events for the
    same learner (e.g. a quiz submission and a "mark complete" clicked together)
    would otherwise race: lost point/chart/progress updates (read-modify-write on
    the user row) and colliding inserts of the same Achievement (both events see
    no achievement, both create it, one rolls back — leaving the badge unrecorded
    even though it "completed"). Locking the user row makes same-user events queue;
    different users still process in parallel.
    """

    if not created:
        return

    event = instance
    configuration = event.configuration
    user = GammaUser.ensure_gamma_user_is_created(user_uid=event.username)

    with transaction.atomic():
        # Re-fetch the user under a row lock for the duration of processing. The
        # internal points/achievement events emitted below re-enter this handler
        # synchronously within this same transaction; re-locking a row the
        # transaction already holds is a no-op, so the recursion does not deadlock.
        user = GammaUser.objects.select_for_update().get(pk=user.pk)

        affected_rules_by_event = Rule.objects.not_completed_by_user(configuration, user)
        rule_filter = RulesFilterService(event)
        affected_rules = rule_filter.filter_rules(affected_rules_by_event)

        for rule in affected_rules:
            for backend in get_gamification_backends():
                backend.process_achievement(rule, event, user)

        # To avoid recursion we limit the calls only for common events.
        if configuration.event_name in EventConfiguration.common_event_names():
            user.run_update_user_pipeline(event)
            # A common (point-earning) event means the learner was active today: award
            # the daily Continuous Learning points and advance their streak. Runs under
            # the same row lock and creates no Event, so it does not re-enter this signal.
            register_active_day(user, event_name=configuration.event_name)

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from achievements.models import Achievement, AchievementRule
from avatars.models import Avatar
from badges.models import Badge
from core.utils import get_gamification_backends
from events.models import Event
from rules.models import Rule
from users.models import GammaUser


class Command(BaseCommand):
    """
    Create the achievements that the shared-rule selection bug starved.

    Until the not_completed_by_user() fix, completing a rule's achievement
    instance under ONE content object (e.g. an avatar) stopped the rule from
    ever being processed again for that user — so a badge sharing the same
    rule never received an achievement. Going forward the fixed selection
    handles this on the user's next matching event; this command repairs users
    retroactively (including ones who may never emit that event type again) by
    replaying each starved user's most recent matching Event through the
    regular gamification backends.

    Accuracy note: replay is exact for rules whose processors derive progress
    from current state (rgg_points_distribution counts the user's total
    points — the known starved case). For purely incremental count rules the
    replayed event seeds one occurrence; historical occurrences are not
    reconstructed.
    """

    help = (
        'Create achievements starved by the shared-rule selection bug by replaying '
        'each affected user\'s latest matching event through the gamification backends. '
        'Exact for state-derived rules (points); seeds a single occurrence for '
        'incremental count rules.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--rule-id',
            action='append',
            type=int,
            dest='rule_ids',
            help='Limit the backfill to these rule ids (repeatable).',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Only report how many (user, rule) pairs would be replayed.',
        )

    def handle(self, *args, **options):
        rules = Rule.objects.exclude(event_configuration=None)
        if options['rule_ids']:
            rules = rules.filter(id__in=options['rule_ids'])

        starved_pairs = set()
        for rule in rules:
            carriers = self._carriers(rule)
            if len(carriers) < 2:
                # Starvation requires the rule to be shared between objects.
                continue

            completed_user_ids = set(
                AchievementRule.objects.filter(
                    rule=rule, status=AchievementRule.Statuses.COMPLETED,
                ).values_list('achievement__user_id', flat=True)
            )
            if not completed_user_ids:
                continue

            for content_type, carrier in carriers:
                user_ids_with_achievement = set(
                    Achievement.objects.filter(
                        content_type=content_type,
                        object_id=carrier.id,
                        user_id__in=completed_user_ids,
                    ).values_list('user_id', flat=True)
                )
                for user_id in completed_user_ids - user_ids_with_achievement:
                    starved_pairs.add((user_id, rule.id))

        self.stdout.write(f'Found {len(starved_pairs)} starved (user, rule) pairs.')
        if options['dry_run'] or not starved_pairs:
            return

        backends = get_gamification_backends()
        rules_by_id = {rule.id: rule for rule in rules}
        replayed = skipped = 0
        for user_id, rule_id in sorted(starved_pairs):
            rule = rules_by_id[rule_id]
            user = GammaUser.objects.get(id=user_id)
            event = (
                Event.objects
                .filter(username=user.user_uid, configuration=rule.event_configuration)
                .order_by('-id')
                .first()
            )
            if event is None:
                skipped += 1
                continue
            for backend in backends:
                backend.process_achievement(rule, event, user)
            replayed += 1

        self.stdout.write(self.style.SUCCESS(
            f'Replayed {replayed} pairs; skipped {skipped} with no matching event.'
        ))

    @staticmethod
    def _carriers(rule):
        """
        Content objects carrying the rule, mirroring what the backends process
        (active badges; avatars in non-draft sets).
        """
        badge_content_type = ContentType.objects.get_for_model(Badge)
        avatar_content_type = ContentType.objects.get_for_model(Avatar)
        return [
            *[(badge_content_type, badge) for badge in Badge.objects.filter(rules=rule, is_active=True)],
            *[(avatar_content_type, avatar) for avatar in Avatar.objects.filter(rules=rule, avatarset__is_draft=False)],
        ]

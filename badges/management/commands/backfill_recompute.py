"""
Post-backfill reconciliation (gamma-side; run in the rgg container).

After an event backfill, reconcile every target badge's holders against the full
stored Event history via achievements.reconciliation.recompute_holders. This:
  * grants the badge to users whose qualifying events predate the badge (or whose
    live processing was interrupted by an ungraceful shutdown — the Event committed
    but its post_save badge grant rolled back; recompute repairs those orphans), and
  * is the mandatory final step of the backfill (see the backfill runbook).

Then it rebuilds the leaderboards, because bulk point/cleanup edits made with
QuerySet.update() bypass the GammaUser pre_save signal that normally keeps the
Redis boards in sync.

Default scope is the placeholder badge category; --all-active covers every active
rule-driven badge (e.g. 'Answerer' on the same problem feed). Idempotent.
"""
from django.conf import settings
from django.core.management.base import BaseCommand

from achievements.reconciliation import recompute_holders
from badges.models import Badge


class Command(BaseCommand):
    help = "Reconcile badge holders from Event history + rebuild leaderboards (post-backfill)."

    def add_arguments(self, parser):
        parser.add_argument('--category', default='Activity (placeholder)',
                            help="Recompute badges in this category (default: %(default)r).")
        parser.add_argument('--all-active', action='store_true',
                            help='Recompute every active rule-driven badge instead of just the category.')
        parser.add_argument('--skip-leaderboard', action='store_true',
                            help='Skip the leaderboard rebuild step.')

    def handle(self, *args, **options):
        if options['all_active']:
            candidates = Badge.objects.filter(is_active=True)
        else:
            candidates = Badge.objects.filter(category=options['category'])
        badges = [b for b in candidates if b.rules.exists()]

        self.stdout.write('Recomputing holders for %d badge(s)...' % len(badges))
        totals = {'granted': 0, 'revoked': 0}
        for badge in badges:
            result = recompute_holders(badge)
            totals['granted'] += len(result.granted)
            totals['revoked'] += len(result.revoked)
            self.stdout.write('  %-32s %s' % ((badge.title or '')[:32], result.summary()))
        self.stdout.write(self.style.SUCCESS(
            'Recompute done: +%d granted, -%d revoked.' % (totals['granted'], totals['revoked'])))

        if options['skip_leaderboard']:
            return
        from leaderboard.repository import ORMLeaderboardMemberDataRepository
        from leaderboard.usecases import (
            ResetLeaderboardsInitializationStatusUseCase,
            ScheduleLeaderboardsInitializationUseCase,
        )
        ResetLeaderboardsInitializationStatusUseCase().execute()
        ScheduleLeaderboardsInitializationUseCase(
            ORMLeaderboardMemberDataRepository(),
        ).execute(settings.LEADERBOARD_INITIALIZATION_BATCH_SIZE)
        self.stdout.write(self.style.SUCCESS('Leaderboard rebuild scheduled (rgg-worker will process it).'))

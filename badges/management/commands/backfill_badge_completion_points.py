"""
Pay a badge's completion points to learners who earned it *before* it was worth anything.

Why this exists
---------------
``Badge.points`` is only ever paid at the moment an achievement completes — by
``AchievementCompletionUseCase`` for rule-driven badges and by ``Badge.award_to_user``
for manual grants. Both pay inside a "first completion only" guard, so raising a badge's
points afterwards is **not** retroactive: every learner who already holds it keeps a
zero-point achievement forever while new earners get the full amount.

That is exactly the situation for the fourteen green "triangle" badges (the six profile
milestones and the eight activity badges), which have carried ``points=0`` since they
were created. Setting a value on them without this command produces a two-tier economy in
which the earliest, most active learners are the only ones who never get paid.

What it does
------------
For each (learner, badge) pair named on the command line, where the learner's achievement
completed before ``--completed-before``, credit the badge's points to
``GammaUser.points`` and to the points timeline, then stamp
``Achievement.completion_points_paid`` so the payment is recorded and never repeated.

Safety
------
* **Dry-run by default.** Prints the projected impact and rolls back. ``--commit`` persists.
* **Explicitly scoped.** You must name the badges and (optionally) their new values. There
  is no "all badges" mode, because most badges *have* already paid their holders and
  sweeping them in would double-credit tens of thousands of learners.
* **Cutoff-guarded.** ``--completed-before`` is required. Achievements completed at or
  after it are skipped: they were earned once the badge already had a value, so the live
  path paid them. Pin one timestamp and reuse it verbatim for every re-run.
* **Idempotent and resumable.** An achievement with ``completion_points_paid`` already set
  is skipped, so a run killed halfway (a container recreate mid-backfill has bitten this
  project before) can simply be re-run. Re-running a finished backfill is a no-op.
* **Race-safe.** Each learner's row is taken with ``select_for_update()``, the same lock
  the live event pipeline uses, so a concurrent award cannot lose this update.
* **Reversible.** ``Badge.revoke_from_user`` reverses ``completion_points_paid``, so a
  learner's backfilled points come back off exactly.

The leaderboard is a Redis ZSET rebuilt by a periodic beat task rather than written at
award time, so standings catch up on their own within about a minute of the run — provided
``rgg-beat`` is up.
"""
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.utils.dateparse import parse_datetime
from django.utils.timezone import is_naive, make_aware

from achievements.models import Achievement
from badges.models import Badge
from users.models import GammaUser

# Credit the points to the day the badge was actually earned rather than to today, so the
# learner's Points Distribution timeline reads as it would have if the badge had been
# worth something all along. ``today`` is offered for the opposite reading: the points
# were granted now, as a one-off correction.
TIMELINE_CHOICES = ('earned', 'today')


class Command(BaseCommand):
    help = (
        'Retroactively pay Badge.points to learners who earned a badge while it was worth '
        'less (dry-run by default).'
    )

    def add_arguments(self, parser):
        scope = parser.add_mutually_exclusive_group(required=True)
        scope.add_argument(
            '--points', dest='points_map', default=None,
            help=(
                'Comma-separated BADGE_ID=POINTS pairs, e.g. "10=50,11=50,29=25". Sets '
                'Badge.points to these values and backfills exactly these badges. The '
                'write is inside the same transaction as the backfill, so a dry-run '
                'rolls the new values back too.'
            ),
        )
        scope.add_argument(
            '--badges', dest='badge_ids', default=None,
            help=(
                'Comma-separated badge ids to backfill using whatever Badge.points each '
                'one already has. Use when the values were set in the admin UI.'
            ),
        )
        parser.add_argument(
            '--completed-before', dest='completed_before', required=True,
            help=(
                'ISO-8601 timestamp. Only achievements completed strictly before this are '
                'paid; anything later was earned after the badge had a value and was paid '
                'by the live path. REQUIRED, and must be kept identical across re-runs.'
            ),
        )
        parser.add_argument(
            '--timeline', choices=TIMELINE_CHOICES, default='earned',
            help=(
                "Which day the points land on in the learner's timeline: 'earned' (default, "
                "the achievement's completion date) or 'today'."
            ),
        )
        parser.add_argument(
            '--commit', action='store_true',
            help='Persist changes. Without it, the command is a dry-run and rolls back.',
        )
        parser.add_argument(
            '--user-uid', dest='user_uid', default=None,
            help='Limit to a single GammaUser by user_uid (useful for a live smoke test).',
        )
        parser.add_argument(
            '--limit', type=int, default=None,
            help='Process at most N learners (useful for a staged rollout).',
        )

    def handle(self, *args, **options):
        commit = options['commit']
        cutoff = self._parse_cutoff(options['completed_before'])
        badge_points = self._resolve_badges(options['points_map'], options['badge_ids'])

        badge_ct = ContentType.objects.get_for_model(Badge)
        achievements = Achievement.objects.filter(
            content_type=badge_ct,
            object_id__in=badge_points,
            completed_at__isnull=False,
            completed_at__lt=cutoff,
            completion_points_paid__isnull=True,
        ).order_by('user_id', 'id')

        user_ids = list(
            achievements.values_list('user_id', flat=True).distinct().order_by('user_id')
        )
        if options['user_uid']:
            user_ids = list(
                GammaUser.objects.filter(pk__in=user_ids, user_uid=options['user_uid'])
                .values_list('pk', flat=True)
            )
        if options['limit'] is not None:
            user_ids = user_ids[:options['limit']]

        self._report_plan(badge_points, cutoff, len(user_ids), achievements)

        processed = paid_rows = total_points = 0

        with transaction.atomic():
            if options['points_map']:
                for badge_id, points in badge_points.items():
                    Badge.objects.filter(pk=badge_id).update(points=points)

            for user_id in user_ids:
                with transaction.atomic():
                    # Same lock the live pipeline takes, so a concurrent award for this
                    # learner serialises behind us instead of overwriting our total.
                    user = GammaUser.objects.select_for_update().get(pk=user_id)
                    rows = list(achievements.filter(user_id=user_id))

                    for achievement in rows:
                        points = badge_points[achievement.object_id]
                        if points:
                            user.update_user_points(points)
                            user.update_user_progress(
                                points,
                                when=achievement.completed_at if options['timeline'] == 'earned' else None,
                            )
                        achievement.completion_points_paid = points
                        achievement.save(update_fields=('completion_points_paid',))
                        total_points += points

                    paid_rows += len(rows)

                processed += 1
                if processed % 500 == 0:
                    self.stdout.write(f'  ... {processed}/{len(user_ids)} learners, +{total_points} points')

            if not commit:
                transaction.set_rollback(True)

        mode = 'COMMITTED' if commit else 'DRY-RUN (rolled back)'
        self.stdout.write(self.style.SUCCESS(
            f'\n{mode}: {processed} learners, {paid_rows} achievements, +{total_points} points.'
        ))
        if not commit and processed:
            self.stdout.write('Re-run with --commit to apply.')
        elif commit and processed:
            self.stdout.write(
                'Leaderboards refresh on the next beat tick (~60s); confirm rgg-beat is running.'
            )

    def _parse_cutoff(self, raw):
        parsed = parse_datetime(raw)
        if parsed is None:
            try:
                parsed = datetime.fromisoformat(raw)
            except ValueError:
                raise CommandError(
                    f'--completed-before: could not parse {raw!r} as an ISO-8601 datetime '
                    '(e.g. "2026-07-20T12:00:00Z").'
                )
        return make_aware(parsed) if is_naive(parsed) else parsed

    def _resolve_badges(self, points_map, badge_ids):
        """Return {badge_id: points} for the requested scope, validating every id exists."""
        if points_map:
            requested = {}
            for chunk in filter(None, (c.strip() for c in points_map.split(','))):
                badge_id, __, points = chunk.partition('=')
                if not points:
                    raise CommandError(f'--points: {chunk!r} is not in BADGE_ID=POINTS form.')
                try:
                    requested[int(badge_id)] = int(points)
                except ValueError:
                    raise CommandError(f'--points: {chunk!r} has a non-integer id or value.')
        else:
            try:
                requested = {
                    int(c.strip()): None
                    for c in badge_ids.split(',') if c.strip()
                }
            except ValueError:
                raise CommandError(f'--badges: {badge_ids!r} is not a comma-separated list of ids.')

        if not requested:
            raise CommandError('No badges given.')

        found = Badge.objects.filter(pk__in=requested).in_bulk()
        missing = sorted(set(requested) - set(found))
        if missing:
            raise CommandError(f'No badge with id(s): {missing}.')

        return {
            badge_id: (points if points is not None else found[badge_id].points)
            for badge_id, points in requested.items()
        }

    def _report_plan(self, badge_points, cutoff, learner_count, achievements):
        self.stdout.write(f'Cutoff: achievements completed before {cutoff.isoformat()}')
        self.stdout.write('Badge                                    points  unpaid achievements')
        for badge in Badge.objects.filter(pk__in=badge_points).order_by('pk'):
            n = achievements.filter(object_id=badge.pk).count()
            self.stdout.write(
                f'  {badge.pk:<4} {str(badge.title)[:34]:<34} {badge_points[badge.pk]:>6}  {n}'
            )
        self.stdout.write(f'Learners affected: {learner_count}\n')

"""
Backfill Continuous Learning streaks/points from each learner's historical activity.

OPTIONAL. The live feature starts every learner's streak fresh from the day it is
enabled. Run this command if you instead want existing learners credited for the active
days they already had — it replays each user's historical active days (distinct calendar
days on which they earned points) through the exact same logic the live path uses, so it
produces the streak state, daily points and milestone badges they would have if the
feature had always been on.

Safety:
  * Dry-run by default — prints the projected impact and rolls everything back. Pass
    ``--commit`` to persist.
  * Skips any user who already has Continuous Learning points (a ``continuous_learning``
    chart bucket), so it never double-credits a user the live feature has already
    touched, and is safe to re-run. Pass ``--force`` to process them anyway.
  * Best run during a quiet period: it does not take the per-user event lock, so a live
    event for the same user mid-backfill could interleave.

Note: retroactive daily points are credited to their real historical dates on the points
timeline, but a milestone badge's bonus points land on today's timeline entry (the badge
is genuinely earned now). The Points Distribution bucket and lifetime total are exact.
"""
from collections import defaultdict

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from events.models import Event, EventConfiguration
from users.continuous_learning import (
    CONTINUOUS_LEARNING_KEY,
    PASSIVE_EVENT_NAMES,
    register_active_day,
)
from users.models import GammaUser


class Command(BaseCommand):
    help = 'Backfill Continuous Learning streaks and points from historical activity (dry-run by default).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--commit', action='store_true',
            help='Persist changes. Without it, the command is a dry-run and rolls back.',
        )
        parser.add_argument(
            '--force', action='store_true',
            help='Also process users who already have Continuous Learning points.',
        )
        parser.add_argument(
            '--user-uid', dest='user_uid', default=None,
            help='Limit to a single GammaUser by user_uid (useful for testing).',
        )
        parser.add_argument(
            '--limit', type=int, default=None,
            help='Process at most N users (useful for a staged rollout).',
        )

    def handle(self, *args, **options):
        commit = options['commit']
        force = options['force']

        common_names = set(EventConfiguration.common_event_names()) - PASSIVE_EVENT_NAMES

        users = GammaUser.objects.all().order_by('id')
        if options['user_uid']:
            users = users.filter(user_uid=options['user_uid'])

        processed = skipped = 0
        total_days = total_points = total_badges = 0

        for user in users.iterator():
            if options['limit'] is not None and processed >= options['limit']:
                break

            if not force and (user.chart or {}).get(CONTINUOUS_LEARNING_KEY):
                skipped += 1
                continue

            active_dates = self._active_dates(user, common_names)
            if not active_dates:
                skipped += 1
                continue

            with transaction.atomic():
                points_before = user.points
                badges_before = self._badge_count(user)

                for activity_date in active_dates:
                    # Re-fetch a fresh instance per day, exactly as the live signal does
                    # for each event: register_active_day's streak-badge completion writes
                    # points on a separate instance, so reusing one stale instance across
                    # days would let a later day's save clobber an earlier day's bonus.
                    day_user = GammaUser.objects.get(pk=user.pk)
                    register_active_day(day_user, activity_date=activity_date, force=True)

                user.refresh_from_db()
                gained_points = user.points - points_before
                gained_badges = self._badge_count(user) - badges_before

                if not commit:
                    transaction.set_rollback(True)

            processed += 1
            total_days += len(active_dates)
            total_points += gained_points
            total_badges += gained_badges
            self.stdout.write(
                f'{user.user_uid}: {len(active_dates)} active days, streak->{user.current_streak}, '
                f'+{gained_points} pts, +{gained_badges} badges'
            )

        mode = 'COMMITTED' if commit else 'DRY-RUN (rolled back)'
        self.stdout.write(self.style.SUCCESS(
            f'\n{mode}: processed {processed} users (skipped {skipped}); '
            f'{total_days} active days, +{total_points} points, +{total_badges} badges total.'
        ))
        if not commit and processed:
            self.stdout.write('Re-run with --commit to apply.')

    @staticmethod
    def _active_dates(user, common_names):
        """Sorted distinct calendar days the user earned points from a non-passive action."""
        events = Event.objects.filter(
            username=user.user_uid,
            configuration__event_type__name__in=common_names,
        ).values_list('created_at', flat=True)

        days = {timezone.localtime(created_at).date() for created_at in events}
        return sorted(days)

    @staticmethod
    def _badge_count(user):
        from django.contrib.contenttypes.models import ContentType
        from achievements.models import Achievement
        from badges.models import Badge

        return Achievement.objects.filter(
            user=user, content_type=ContentType.objects.get_for_model(Badge),
        ).count()

"""
Detect rushed "Mark as complete" gaming and flag it (staff-only) or claw back the
gamification points it earned. Run daily (cron).

Reads its policy from the anti-gaming Rule seeded by ``initialize_anti_gaming``:
    filters["course"]                -> OR allowlist of course_ids the rule applies to
    action["rgg_rushed_completion"]  -> { mode, gap_sec, run_min, clawback_per_block,
                                          min_engagement_events }

For each (learner, allowlisted course) it analyses the learner's own gamma Event history
(no LMS DB access needed — gamma already receives these from the bridge):
  - rushing  : `edx_done_toggled` events whose gap to the previous one is <= gap_sec form
               maximal runs; a run of >= run_min blocks is a "rush burst".
  - engaged  : count of `stop_video` (watched-to-end) + `edx_grades_problem_submitted`
               events in the course — independent signals a learner can't fake by clicking
               "done". (`stop_video` is the segment-accurate watch signal, so this needs
               neither ENABLE_COMPLETION_TRACKING nor the saved_video_position proxy.)
A learner is CONFIRMED gaming when they have a rush burst AND too little engagement —
i.e. they clicked through without watching/solving.

  mode="flag"  : record an AntiGamingPenalty (points_docked=0) + report. Never touch points.
  mode="dock"  : same record + claw back  rushed_blocks * clawback_per_block  points (= the
                 points those rushed done-toggles earned; net-zero gain, not a punitive nuke).

Idempotent + reversible: each run reconciles every learner to their freshly-computed state
via the delta to the stored dock; a learner who stops qualifying (no longer rushing, or has
since watched the videos) has their docked points restored and the record removed. Flip the
rule's mode flag<->dock for a one-field move from calibration to enforcement.
"""
from collections import defaultdict

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.timezone import now

from badges.models import AntiGamingPenalty
from events.enums import EdxCommonEventTypes, RggInternalEventTypes
from events.models import Event, EventConfiguration
from rules.models import Rule
from users.models import GammaUser

DONE = EdxCommonEventTypes.EDX_DONE_TOGGLED.value
VIDEO = EdxCommonEventTypes.EDX_STOP_VIDEO.value
PROBLEM = EdxCommonEventTypes.EDX_GRADES_PROBLEM_SUBMITTED.value
RULE_EVENT = RggInternalEventTypes.RGG_RUSHED_COMPLETION.value


def rush_profile(timestamps, gap_sec, run_min):
    """Sorted done-toggle datetimes -> (rushed_blocks, longest_run).

    rushed_blocks = total blocks inside maximal <=gap_sec runs whose length >= run_min."""
    n = len(timestamps)
    if n == 0:
        return 0, 0
    rushed = 0
    longest = run = 1
    for i in range(1, n):
        if (timestamps[i] - timestamps[i - 1]).total_seconds() <= gap_sec:
            run += 1
        else:
            if run >= run_min:
                rushed += run
            run = 1
        longest = max(longest, run)
    if run >= run_min:
        rushed += run
    return rushed, longest


class Command(BaseCommand):
    help = 'Detect rushed Mark-as-complete gaming; flag (staff) or dock (claw-back). Run daily.'

    def add_arguments(self, parser):
        parser.add_argument('--mode', choices=['flag', 'dock'], default=None,
                            help='Override the rule mode for this run.')
        parser.add_argument('--dry-run', action='store_true',
                            help='Compute + report only; never write points or records.')
        parser.add_argument('--force', action='store_true',
                            help='Run even if RGG_ANTI_GAMING_ENABLED is off.')

    def handle(self, *args, **options):
        if not getattr(settings, 'RGG_ANTI_GAMING_ENABLED', False) and not options['force']:
            self.stdout.write(self.style.WARNING(
                'RGG_ANTI_GAMING_ENABLED is off; pass --force to run anyway. Exiting.'))
            return

        config = EventConfiguration.objects.filter(event_type__name=RULE_EVENT).first()
        rule = Rule.objects.filter(event_configuration=config).first() if config else None
        if rule is None:
            raise CommandError('Anti-gaming rule not found. Run `initialize_anti_gaming` first.')

        allowlist = rule.filters.get('course') or []
        if not allowlist:
            self.stdout.write(self.style.WARNING('Rule course allowlist is empty; nothing to do.'))
            return

        policy = rule.action.get(RULE_EVENT, {})
        mode = options['mode'] or policy.get('mode', 'flag')
        gap = int(policy.get('gap_sec', 30))
        run_min = int(policy.get('run_min', 10))
        per_block = int(policy.get('clawback_per_block', 5))
        min_eng = int(policy.get('min_engagement_events', 3))
        dry = options['dry_run']

        self.stdout.write(
            f'anti-gaming: mode={mode} dry_run={dry} gap={gap}s run_min={run_min} '
            f'clawback/block={per_block} min_engagement={min_eng} courses={len(allowlist)}')

        totals = defaultdict(int)
        for course_id in allowlist:
            usernames = list(Event.objects.filter(
                course_id=course_id, configuration__event_type__name=DONE,
            ).values_list('username', flat=True).distinct())

            for uid in usernames:
                dts = list(Event.objects.filter(
                    username=uid, course_id=course_id,
                    configuration__event_type__name=DONE,
                ).order_by('created_at').values_list('created_at', flat=True))
                rushed_blocks, longest = rush_profile(dts, gap, run_min)

                if longest < run_min:
                    confirmed = False
                else:
                    engagement = Event.objects.filter(
                        username=uid, course_id=course_id,
                        configuration__event_type__name__in=[VIDEO, PROBLEM],
                    ).count()
                    confirmed = engagement < min_eng

                user = GammaUser.objects.filter(user_uid=uid).first()
                if user is None:
                    continue

                if confirmed:
                    totals['confirmed'] += 1
                    target = rushed_blocks * per_block if mode == 'dock' else 0
                    self.stdout.write(
                        f'  {"DRY " if dry else ""}{mode.upper()} {uid} {course_id} '
                        f'run={longest} rushed_blocks={rushed_blocks} dock={target}')
                    if not dry:
                        self._apply(user, course_id, target, rushed_blocks, longest, mode)
                elif not dry:
                    if self._clear(user, course_id):
                        totals['restored'] += 1

        self.stdout.write(self.style.SUCCESS(
            f'done: confirmed={totals["confirmed"]} restored={totals["restored"]}'))

    @transaction.atomic
    def _apply(self, user, course_id, target_dock, rushed_blocks, longest, mode):
        """Reconcile the learner's dock to ``target_dock`` (idempotent)."""
        penalty, _created = AntiGamingPenalty.objects.select_for_update().get_or_create(
            user=user, course_id=course_id)
        delta = target_dock - penalty.points_docked   # >0 => dock more, <0 => give some back
        if delta:
            user.update_user_points(-delta)
            user.update_user_progress(-delta)
        penalty.points_docked = target_dock
        penalty.rushed_blocks = rushed_blocks
        penalty.longest_run = longest
        penalty.mode = mode
        penalty.evaluated_at = now()
        penalty.save()

    @transaction.atomic
    def _clear(self, user, course_id):
        """Reverse and remove a penalty for a learner who no longer qualifies."""
        penalty = AntiGamingPenalty.objects.select_for_update().filter(
            user=user, course_id=course_id).first()
        if penalty is None:
            return False
        if penalty.points_docked:
            user.update_user_points(penalty.points_docked)
            user.update_user_progress(penalty.points_docked)
        penalty.delete()
        return True

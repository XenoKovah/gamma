"""
Seed the anti-gaming "rushed Mark-as-complete" policy Rule (idempotent).

Creates the internal ``rgg_rushed_completion`` event type/configuration and a single
``Rule`` that holds the policy. This Rule is the admin-editable control surface consumed
by the daily ``process_anti_gaming`` command (it is NOT fired by the live event engine):

    filters = {"course": [ ...course_ids... ]}   # OR allowlist — WHICH classes it applies to
    action  = {"rgg_rushed_completion": {
        "count": 1,
        "mode": "flag",            # "flag" = staff-only record | "dock" = claw back points
        "gap_sec": 30,             # consecutive done-clicks <= this apart are a "burst"
        "run_min": 10,             # a burst of >= this many blocks counts as rushing
        "clawback_per_block": 5,   # = the edx_done_toggled award; dock = rushed_blocks * this
        "min_engagement_events": 3 # >= this many stop_video + problem-submit events => engaged
    }}

To deploy: add course_ids to filters["course"] (only courses with a real engagement
signal — videos/problems; never the GDB-style setup courses), run in flag mode, calibrate,
then flip action[...]["mode"] flag->dock. Re-running only creates missing pieces; an
existing rule's config is left intact.
"""
import json

from django.core.management.base import BaseCommand

from events.enums import RggInternalEventTypes
from events.models import EventConfiguration, EventType
from rules.models import Rule

EVENT_NAME = RggInternalEventTypes.RGG_RUSHED_COMPLETION.value
DEFAULT_POLICY = {
    'count': 1,
    'mode': 'flag',
    'gap_sec': 30,
    'run_min': 10,
    'clawback_per_block': 5,
    'min_engagement_events': 3,
}


class Command(BaseCommand):
    help = 'Create the anti-gaming rushed-completion event type + policy Rule (idempotent).'

    def handle(self, *args, **options):
        event_type, _created = EventType.objects.get_or_create(name=EVENT_NAME)
        config, _created = EventConfiguration.objects.get_or_create(
            event_type=event_type,
            defaults={'title': str(RggInternalEventTypes.RGG_RUSHED_COMPLETION.title), 'award': 0},
        )

        rule = Rule.objects.filter(event_configuration=config).first()
        if rule is None:
            rule = Rule.objects.create(
                event_configuration=config,
                action={EVENT_NAME: dict(DEFAULT_POLICY)},
                filters={'course': []},
            )
            self.stdout.write(self.style.SUCCESS(
                'Created anti-gaming rule (mode=flag, empty course allowlist).'))
        else:
            self.stdout.write(
                f'Anti-gaming rule already exists: action={json.dumps(rule.action)} '
                f'filters={json.dumps(rule.filters)}')

        self.stdout.write(
            'Next: add course_ids to filters["course"], run `process_anti_gaming` in flag '
            'mode, calibrate, then set action["%s"]["mode"]="dock".' % EVENT_NAME)

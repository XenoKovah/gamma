"""
Create the Continuous Learning streak badges (idempotent).

Seeds both kinds of streak badge (see users.continuous_learning.STREAK_KINDS):

  * "{N} day streak"     — N consecutive calendar days.
  * "{N} weekday streak" — N consecutive weekdays, for learners who study Mon-Fri and
                           would otherwise reset every Monday.

Run once per environment as part of deploying the Continuous Learning feature, before
(or alongside) enabling it, so that learners crossing a milestone have a badge to earn.
Re-run it after adding a new streak kind or milestone to create just the missing pieces.

Each badge is rule-driven (like the points-threshold badges): a single rule with action
``{<the kind's event>: {count: N}}`` against that kind's internal event type. The rules
engine then renders the in-progress ring (streak / N) and awards the badge — paying its
completion points — when the streak reaches N. Re-running is safe: the event types,
badges and rules are matched and only missing pieces are created; existing badges keep
their title, description, points and any hand-uploaded image.
"""
import os

from django.core.files import File
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from badges.models import Badge
from events.models import EventConfiguration, EventType
from rules.models import Rule
from users.continuous_learning import (
    CONTINUOUS_LEARNING_CATEGORY,
    STREAK_KINDS,
    STREAK_MILESTONES,
)

IMAGES_DIR = os.path.join(os.path.dirname(__file__), '_continuous_learning_images')


class Command(BaseCommand):
    help = 'Creates the Continuous Learning streak badges (and their rules) for every streak kind.'

    def handle(self, *args, **options):
        for kind in STREAK_KINDS:
            self.stdout.write(f'{kind.key} streaks ({kind.event_name}):')
            streak_config = self._ensure_streak_event_configuration(kind)

            for days, bonus in STREAK_MILESTONES:
                slug = kind.badge_slug(days)

                badge, created = Badge.objects.get_or_create(
                    slug=slug,
                    defaults={
                        'title': kind.badge_title(days),
                        'description': kind.badge_description(days),
                        'points': bonus,
                        'category': CONTINUOUS_LEARNING_CATEGORY,
                        'is_active': True,
                    },
                )
                self.stdout.write(
                    self.style.SUCCESS(f'  Created badge: {slug} (+{bonus} pts)') if created
                    else f'  Badge already exists: {slug}'
                )

                self._ensure_badge_rule(badge, streak_config, kind, days)
                self._ensure_badge_image(badge, days, slug)

    def _ensure_streak_event_configuration(self, kind):
        """Create the kind's internal event type + configuration (award 0), idempotently."""
        event_type, _ = EventType.objects.get_or_create(name=kind.event_name)
        config, _ = EventConfiguration.objects.get_or_create(
            event_type=event_type,
            defaults={'title': str(kind.event_type.title), 'award': 0},
        )
        return config

    def _ensure_badge_rule(self, badge, streak_config, kind, days):
        """Attach a streak rule (goal = ``days`` days this kind counts) to the badge."""
        action = {kind.event_name: {'count': days}}
        rule = Rule.objects.filter(event_configuration=streak_config, action=action).first()
        if rule is None:
            rule = Rule.objects.create(event_configuration=streak_config, action=action, filters={})
            self.stdout.write(self.style.SUCCESS(f'    created rule (count={days})'))
        badge.rules.add(rule)

    def _ensure_badge_image(self, badge, days, slug):
        """
        Attach the badge image only if it has none yet (never clobber a hand-uploaded one).

        All streak kinds share one piece of artwork per milestone, so prefer whatever a
        sibling badge for the same milestone is *currently* showing over the file bundled
        here. The day badges' images had already been replaced by hand in the badge
        editor, so seeding the weekday badges from the bundled PNG gave them the
        superseded art while their day counterparts showed the newer version. Falling
        back to the bundled file only when no sibling has an image keeps a from-scratch
        environment working exactly as before.
        """
        if badge.image:
            return

        sibling_artwork = self._sibling_milestone_image(days, exclude_slug=slug)
        if sibling_artwork is not None:
            badge.image.save(f'{slug}.png', sibling_artwork, save=True)
            self.stdout.write(self.style.SUCCESS(f'    copied sibling artwork for {slug}'))
            return

        image_path = os.path.join(IMAGES_DIR, f'{days}_day_streak.png')
        if os.path.exists(image_path):
            with open(image_path, 'rb') as fh:
                badge.image.save(f'{slug}.png', File(fh), save=True)
            self.stdout.write(self.style.SUCCESS(f'    attached image for {slug}'))
        else:
            self.stdout.write(self.style.WARNING(f'    image not found for {slug}: {image_path}'))

    @staticmethod
    def _sibling_milestone_image(days, exclude_slug):
        """The artwork another kind's badge for the same milestone already carries, if any."""
        for kind in STREAK_KINDS:
            sibling_slug = kind.badge_slug(days)
            if sibling_slug == exclude_slug:
                continue
            sibling = Badge.objects.filter(slug=sibling_slug).exclude(image='').first()
            if sibling is not None and sibling.image:
                sibling.image.open('rb')
                try:
                    return ContentFile(sibling.image.read())
                finally:
                    sibling.image.close()
        return None

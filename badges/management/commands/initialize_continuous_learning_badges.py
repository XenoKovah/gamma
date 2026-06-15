"""
Create the "{N} day streak" Continuous Learning badges (idempotent).

Run once per environment as part of deploying the Continuous Learning feature, before
(or alongside) enabling it, so that learners crossing a milestone have a badge to earn.

Each badge is rule-driven (like the points-threshold badges): a single rule with action
``{rgg_continuous_learning_streak: {count: N}}`` against the internal
``rgg_continuous_learning_streak`` event type. The rules engine then renders the
in-progress ring (current_streak / N) and awards the badge — paying its completion points
— when the streak reaches N. Re-running is safe: the event type, badges and rules are
matched and only missing pieces are created.
"""
import os

from django.core.files import File
from django.core.management.base import BaseCommand

from badges.models import Badge
from events.enums import RggInternalEventTypes
from events.models import EventConfiguration, EventType
from rules.models import Rule
from users.continuous_learning import (
    CONTINUOUS_LEARNING_CATEGORY,
    STREAK_MILESTONES,
    streak_badge_description,
    streak_badge_slug,
    streak_badge_title,
)

IMAGES_DIR = os.path.join(os.path.dirname(__file__), '_continuous_learning_images')
STREAK_EVENT_NAME = RggInternalEventTypes.RGG_CONTINUOUS_LEARNING_STREAK.value


class Command(BaseCommand):
    help = 'Creates the "{N} day streak" badges (and their rules) used by Continuous Learning.'

    def handle(self, *args, **options):
        streak_config = self._ensure_streak_event_configuration()

        for days, bonus in STREAK_MILESTONES:
            slug = streak_badge_slug(days)

            badge, created = Badge.objects.get_or_create(
                slug=slug,
                defaults={
                    'title': streak_badge_title(days),
                    'description': streak_badge_description(days),
                    'points': bonus,
                    'category': CONTINUOUS_LEARNING_CATEGORY,
                    'is_active': True,
                },
            )
            self.stdout.write(
                self.style.SUCCESS(f'Created badge: {slug} (+{bonus} pts)') if created
                else f'Badge already exists: {slug}'
            )

            self._ensure_badge_rule(badge, streak_config, days)
            self._ensure_badge_image(badge, days, slug)

    def _ensure_streak_event_configuration(self):
        """Create the internal streak event type + configuration (award 0), idempotently."""
        event_type, _ = EventType.objects.get_or_create(name=STREAK_EVENT_NAME)
        config, _ = EventConfiguration.objects.get_or_create(
            event_type=event_type,
            defaults={'title': str(RggInternalEventTypes.RGG_CONTINUOUS_LEARNING_STREAK.title), 'award': 0},
        )
        return config

    def _ensure_badge_rule(self, badge, streak_config, days):
        """Attach a streak rule (goal = ``days`` consecutive active days) to the badge."""
        action = {STREAK_EVENT_NAME: {'count': days}}
        rule = Rule.objects.filter(event_configuration=streak_config, action=action).first()
        if rule is None:
            rule = Rule.objects.create(event_configuration=streak_config, action=action, filters={})
            self.stdout.write(self.style.SUCCESS(f'  created rule (count={days})'))
        badge.rules.add(rule)

    def _ensure_badge_image(self, badge, days, slug):
        """Attach the badge image only if it has none yet (never clobber a hand-uploaded one)."""
        if badge.image:
            return
        image_path = os.path.join(IMAGES_DIR, f'{days}_day_streak.png')
        if os.path.exists(image_path):
            with open(image_path, 'rb') as fh:
                badge.image.save(f'{slug}.png', File(fh), save=True)
            self.stdout.write(self.style.SUCCESS(f'  attached image for {slug}'))
        else:
            self.stdout.write(self.style.WARNING(f'  image not found for {slug}: {image_path}'))

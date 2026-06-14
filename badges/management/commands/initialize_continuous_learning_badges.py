"""
Create the "{N} day streak" Continuous Learning badges (idempotent).

Run once per environment as part of deploying the Continuous Learning feature, before
(or alongside) enabling it, so that learners crossing a milestone have a badge to earn.
Re-running is safe: badges are matched by slug and only missing pieces are filled in.
"""
import os

from django.core.files import File
from django.core.management.base import BaseCommand

from badges.models import Badge
from users.continuous_learning import (
    CONTINUOUS_LEARNING_CATEGORY,
    STREAK_MILESTONES,
    streak_badge_description,
    streak_badge_slug,
    streak_badge_title,
)

IMAGES_DIR = os.path.join(os.path.dirname(__file__), '_continuous_learning_images')


class Command(BaseCommand):
    help = 'Creates the "{N} day streak" badges used by the Continuous Learning feature.'

    def handle(self, *args, **options):
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

            if created:
                self.stdout.write(self.style.SUCCESS(f'Created badge: {slug} (+{bonus} pts)'))
            else:
                self.stdout.write(f'Badge already exists: {slug}')

            # Attach the badge image only if it has none yet (never clobber a hand-uploaded one).
            if not badge.image:
                image_path = os.path.join(IMAGES_DIR, f'{days}_day_streak.png')
                if os.path.exists(image_path):
                    with open(image_path, 'rb') as fh:
                        badge.image.save(f'{slug}.png', File(fh), save=True)
                    self.stdout.write(self.style.SUCCESS(f'  attached image for {slug}'))
                else:
                    self.stdout.write(self.style.WARNING(f'  image not found for {slug}: {image_path}'))

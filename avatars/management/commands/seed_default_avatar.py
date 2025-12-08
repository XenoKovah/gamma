"""
Management command to seed default avatars.
"""

import os
from typing import List

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from achievements.types import AchievementTypes
from avatars.constants import AVATAR_STAGES_MAX
from avatars.models import Avatar, AvatarSet
from events.enums import RggInternalEventTypes
from events.models import EventConfiguration
from events.services import get_event_configuration_service
from rules.models import Rule

AVATAR_ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'assets')
AVATAR_TITLE = 'Azulejo Tile'
AVATAR_SET_TITLE = 'Azulejo Tiles'
AVATAR_PATH_NAME = 'azulejo-tile'
AVATAR_FILE_PATH = 'azulejo-tile-{}.svg'
AVATAR_FILE_DEFAULT_PATH = 'default.svg'


class Command(BaseCommand):
    help = 'Create default evolution avatars with rules preset.'

    def handle(self, *args, **options):
        """
        Seed default avatars and avatar set.
        """
        self.stdout.write(self.style.HTTP_INFO(f'Seeding {AVATAR_STAGES_MAX} avatar stages...'))
        avatar_objects = []
        for stage in range(1, AVATAR_STAGES_MAX + 1):
            asset_path = self.get_asset_path(stage)
            if not asset_path:
                self.stdout.write(self.style.ERROR(f'No avatar image found for stage {stage}'))
                return
            title = f'{AVATAR_TITLE} - Stage {stage}'
            avatar = self.create_avatar(title=title, stage=stage, asset_path=asset_path)
            avatar_objects.append(avatar)

        self.create_avatar_set(title=AVATAR_SET_TITLE, avatars=avatar_objects)
        self.stdout.write(self.style.SUCCESS('Default avatar seeding completed successfully.'))

    def get_asset_path(self, stage: int) -> str:
        """
        Get the file path for the avatar image corresponding to the given stage.
        """
        stage_filename = AVATAR_FILE_PATH.format(stage)
        stage_path = os.path.join(AVATAR_ASSETS_DIR, AVATAR_PATH_NAME, stage_filename)
        if os.path.exists(stage_path):
            return stage_path
        fallback_path = os.path.join(AVATAR_ASSETS_DIR, AVATAR_FILE_DEFAULT_PATH)
        return fallback_path if os.path.exists(fallback_path) else None

    def create_avatar(self, title: str, stage: int, asset_path: str) -> Avatar:
        """
        Create an Avatar only if it does not already exist.
        """
        avatar, created = Avatar.objects.get_or_create(
            title=title,
            stage=stage,
            defaults={
                'description': f'System default avatar for stage {stage}',
            },
        )

        if not created:
            self.stdout.write(self.style.WARNING(f'Avatar for stage {stage} already exists. Skipping update.'))
            return avatar

        # Attach image only if missing and only if not default
        if not avatar.image and not asset_path.endswith('default.svg'):
            with open(asset_path, 'rb') as f:
                content = f.read()
            avatar.image.save(os.path.basename(asset_path), ContentFile(content), save=True)
            self.stdout.write(self.style.SUCCESS(f'Attached image for stage {stage}'))
        elif not avatar.image:
            self.stdout.write(self.style.WARNING(f'No specific image for stage {stage}, default image not attached.'))

        self.add_default_rules_to_avatar(avatar, stage)
        return avatar

    def add_default_rules_to_avatar(self, avatar: Avatar, stage: int) -> None:
        """
        Add default rules to the avatar for the given stage using ORM create/get.
        """
        event_service = get_event_configuration_service(AchievementTypes.AVATAR)

        if not event_service.is_allowed(RggInternalEventTypes.RGG_POINTS_DISTRIBUTION):
            self.stdout.write(self.style.WARNING('Event type not allowed for avatar rule creation.'))
            return

        event_configuration = EventConfiguration.objects.get(
            event_type__name=RggInternalEventTypes.RGG_POINTS_DISTRIBUTION.value
        )

        stage_points = {
            1: 50,
            2: 100,
            3: 200,
            4: 350,
            5: 500,
        }
        points = stage_points.get(stage, stage * 50)  # fallback for unexpected stages

        rule, __ = Rule.objects.get_or_create(
            event_configuration=event_configuration,
            action={RggInternalEventTypes.RGG_POINTS_DISTRIBUTION.value: {'points': points}},
            filters={},
        )

        avatar.rules.set([rule])

    def create_avatar_set(self, title: str, avatars: List[Avatar]) -> AvatarSet:
        """
        Create an AvatarSet with the given title and avatars.
        """
        avatar_set, created = AvatarSet.objects.get_or_create(title=title)
        avatar_set.avatars.set(avatars)
        avatar_set.is_draft = False
        avatar_set.save()
        if created:
            self.stdout.write(self.style.SUCCESS(f'AvatarSet created: {title}'))
        return avatar_set
